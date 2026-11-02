import importlib.util
import shutil
import sqlite3
import sys
import tempfile
import unittest
import uuid
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TodoTitles(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles = []
        self.inputs = {}
        self.spans = []
        self.in_title = False
        self.in_span = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h3' and attrs.get('class') == 'todo-title':
            self.in_title = True
        if tag == 'input' and 'name' in attrs:
            self.inputs[attrs['name']] = attrs.get('value', '')
        if tag == 'span':
            self.in_span = True

    def handle_data(self, data):
        if self.in_title:
            self.titles.append(data)
        if self.in_span:
            self.spans.append(data)

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_title = False
        if tag == 'span':
            self.in_span = False


def titles(response):
    parser = TodoTitles()
    parser.feed(response.get_data(as_text=True))
    return parser.titles


class AssigneeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        shutil.copy(ROOT / 'app.py', self.root / 'app.py')
        shutil.copytree(ROOT / 'templates', self.root / 'templates')

    def load_app(self):
        name = f'todo_test_{uuid.uuid4().hex}'
        spec = importlib.util.spec_from_file_location(name, self.root / 'app.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        self.addCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(module)
        module.app.config['TESTING'] = True

        def dispose():
            with module.app.app_context():
                module.db.session.remove()
                module.db.engine.dispose()

        self.addCleanup(dispose)
        return module

    def test_normalize_email_preserves_local_part_and_invalid_values(self):
        app = self.load_app()
        for value, expected in [
            (None, None), ('', ''), ('invalid', 'invalid'),
            ('User@EXAMPLE.COM', 'User@example.com'),
            ('a@b@EXAMPLE.COM', 'a@b@example.com'),
        ]:
            with self.subTest(value=value):
                self.assertEqual(app.normalize_email(value), expected)

    def test_edit_normalizes_domain_and_preserves_invalid_nonblank_value(self):
        app = self.load_app()
        with app.app.app_context():
            todo = app.Todo(title='Edit me')
            app.db.session.add(todo)
            app.db.session.commit()
            todo_id = todo.id
        client = app.app.test_client()
        for value, expected in [
            ('  User@EXAMPLE.COM  ', 'User@example.com'),
            ('  not-an-email  ', 'not-an-email'),
        ]:
            with self.subTest(value=value):
                response = client.post(f'/edit/{todo_id}', data={'assignee_email': value})
                self.assertEqual(response.status_code, 302)
                with app.app.app_context():
                    self.assertEqual(app.db.session.get(app.Todo, todo_id).assignee_email, expected)

    def test_blank_edit_clears_assignee_and_omitted_edit_preserves_it(self):
        app = self.load_app()
        with app.app.app_context():
            todo = app.Todo(title='Edit me', assignee_email='User@example.com')
            app.db.session.add(todo)
            app.db.session.commit()
            todo_id = todo.id
        client = app.app.test_client()
        response = client.get(f'/edit/{todo_id}')
        self.assertEqual(response.status_code, 200)
        page = TodoTitles()
        page.feed(response.get_data(as_text=True))
        self.assertEqual(page.inputs['assignee_email'], 'User@example.com')
        response = client.post(f'/edit/{todo_id}', data={'title': 'Updated'})
        self.assertEqual(response.status_code, 302)
        with app.app.app_context():
            todo = app.db.session.get(app.Todo, todo_id)
            self.assertEqual(todo.assignee_email, 'User@example.com')
        for value in ('', '   '):
            with self.subTest(value=value):
                with app.app.app_context():
                    app.db.session.get(app.Todo, todo_id).assignee_email = 'User@example.com'
                    app.db.session.commit()
                response = client.post(f'/edit/{todo_id}', data={'assignee_email': value})
                self.assertEqual(response.status_code, 302)
                with app.app.app_context():
                    self.assertIsNone(app.db.session.get(app.Todo, todo_id).assignee_email)

    def test_add_with_omitted_assignee_creates_unassigned_todo(self):
        app = self.load_app()
        response = app.app.test_client().post('/add', data={'title': 'New todo'})
        self.assertEqual(response.status_code, 302)
        with app.app.app_context():
            self.assertIsNone(app.Todo.query.filter_by(title='New todo').one().assignee_email)

    def test_filter_exact_match_domain_normalization_and_descending_order(self):
        app = self.load_app()
        with app.app.app_context():
            app.db.session.add_all([
                app.Todo(title='Old match', assignee_email='User@example.com',
                         created_at=datetime(2024, 1, 1)),
                app.Todo(title='New match', assignee_email='User@example.com',
                         created_at=datetime(2024, 1, 3)),
                app.Todo(title='Partial', assignee_email='User@example.com.extra',
                         created_at=datetime(2024, 1, 4)),
                app.Todo(title='Different local case', assignee_email='user@example.com',
                         created_at=datetime(2024, 1, 2)),
                app.Todo(title='Unassigned', created_at=datetime(2024, 1, 5)),
            ])
            app.db.session.commit()
        client = app.app.test_client()
        filtered = client.get('/', query_string={'assignee': '  User@EXAMPLE.COM  '})
        self.assertEqual(filtered.status_code, 200)
        self.assertEqual(titles(filtered), ['New match', 'Old match'])
        page = TodoTitles()
        page.feed(filtered.get_data(as_text=True))
        self.assertEqual(page.inputs['assignee'], 'User@EXAMPLE.COM')
        self.assertEqual(page.spans, ['User@example.com', 'User@example.com'])
        normalized = client.get('/', query_string={'assignee': 'User@example.com'})
        self.assertEqual(normalized.status_code, 200)
        self.assertEqual(titles(normalized), ['New match', 'Old match'])
        page = TodoTitles()
        page.feed(normalized.get_data(as_text=True))
        self.assertEqual(page.inputs['assignee'], 'User@example.com')
        self.assertEqual(page.spans, ['User@example.com', 'User@example.com'])
        for query in ({}, {'assignee': '   '}):
            with self.subTest(query=query):
                response = client.get('/', query_string=query)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(titles(response), [
                    'Unassigned', 'Partial', 'New match', 'Different local case', 'Old match',
                ])

    def test_existing_schema_migration_preserves_rows_and_is_repeatable(self):
        instance = self.root / 'instance'
        instance.mkdir()
        database = instance / 'todos.db'
        with sqlite3.connect(database) as connection:
            connection.execute('''CREATE TABLE todo (
                id INTEGER PRIMARY KEY, title VARCHAR(200) NOT NULL,
                description TEXT, deadline DATETIME, completed BOOLEAN,
                completed_at DATETIME, created_at DATETIME
            )''')
            connection.execute(
                "INSERT INTO todo (id, title, description, completed, created_at) "
                "VALUES (1, 'Existing', 'Keep me', 0, '2024-01-01 00:00:00')"
            )
        app = self.load_app()
        with app.app.app_context():
            todo = app.db.session.get(app.Todo, 1)
            self.assertEqual((todo.title, todo.description, todo.assignee_email),
                             ('Existing', 'Keep me', None))
            todo.assignee_email = 'User@example.com'
            app.db.session.commit()
        reloaded = self.load_app()
        with reloaded.app.app_context():
            todo = reloaded.db.session.get(reloaded.Todo, 1)
            self.assertEqual((todo.title, todo.description, todo.assignee_email),
                             ('Existing', 'Keep me', 'User@example.com'))
        with sqlite3.connect(database) as connection:
            columns = [row[1] for row in connection.execute('PRAGMA table_info(todo)')]
            self.assertEqual(columns.count('assignee_email'), 1)


if __name__ == '__main__':
    unittest.main()
