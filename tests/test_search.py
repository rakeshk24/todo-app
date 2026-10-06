import importlib.util
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from flask import Flask


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance = tempfile.TemporaryDirectory()
        root = Path(__file__).resolve().parents[1]
        flask_app = Flask('app', root_path=str(root), instance_path=cls.instance.name)
        spec = importlib.util.spec_from_file_location('search_test_app', root / 'app.py')
        cls.module = importlib.util.module_from_spec(spec)
        with patch('flask.Flask', return_value=flask_app):
            spec.loader.exec_module(cls.module)
        cls.app = cls.module.app
        cls.app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            cls.module.db.session.remove()
            cls.module.db.engine.dispose()
        cls.instance.cleanup()

    def setUp(self):
        self.context = self.app.app_context()
        self.context.push()
        self.addCleanup(self.context.pop)
        self.module.db.drop_all()
        self.module.db.create_all()
        self.client = self.app.test_client()

    def add(self, title, **fields):
        todo = self.module.Todo(title=title, **fields)
        self.module.db.session.add(todo)
        self.module.db.session.commit()
        return todo.id

    def search(self, query):
        response = self.client.get('/search', query_string={'q': query})
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def test_literal_wildcards_and_escape_in_both_fields(self):
        for term in ['%', '_', '!', '!%_', '\\']:
            with self.subTest(term=term):
                title_id = self.add('title ' + term)
                description_id = self.add('description match', description='text ' + term)
                self.add('unrelated', description='no special characters')
                self.assertEqual(
                    {todo['id'] for todo in self.search(term)}, {title_id, description_id}
                )
                self.module.db.session.query(self.module.Todo).delete()
                self.module.db.session.commit()

    def test_case_insensitive_substring_and_no_matches(self):
        title_id = self.add('A Mixed TITLE')
        description_id = self.add('other', description='mixed Description')
        self.assertEqual(
            {todo['id'] for todo in self.search('iXeD')}, {title_id, description_id}
        )
        self.assertEqual(self.search('absent'), [])

    def test_limit_order_and_initial_list(self):
        start = datetime(2026, 1, 1)
        for i in range(55):
            self.add(f'broad {i}', created_at=start + timedelta(minutes=i))
        expected = [f'broad {i}' for i in range(54, 4, -1)]
        for query in ['', 'broad']:
            self.assertEqual([todo['title'] for todo in self.search(query)], expected)
        html = self.client.get('/').get_data(as_text=True)
        self.assertEqual(html.count('class="todo-item '), 50)
        self.assertIn('Showing up to 50 newest todos.', html)
        self.assertIn('aria-label="Search todos"', html)

    def test_result_count_log_excludes_query_and_address(self):
        self.add('private search term')
        with self.assertLogs(self.app.logger, level='INFO') as logs:
            self.search('private search term')
        self.assertIn('Search returned 1 results', logs.output[0])
        self.assertNotIn('private search term', logs.output[0])
        self.assertNotIn('127.0.0.1', logs.output[0])

    def test_completed_fields_remain_available(self):
        when = datetime(2026, 1, 2, 12, 30)
        todo_id = self.add('done', completed=True, completed_at=when, deadline=when)
        result = self.search('done')[0]
        self.assertEqual(result['id'], todo_id)
        self.assertTrue(result['completed'])
        self.assertEqual(result['completed_at'], '2026-01-02 12:30')
        self.assertEqual(result['deadline'], '2026-01-02 12:30')


if __name__ == '__main__':
    unittest.main()
