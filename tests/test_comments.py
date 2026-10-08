import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


DATABASE_DIRECTORY = tempfile.TemporaryDirectory()
os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(DATABASE_DIRECTORY.name) / 'tests.db')

from app import app, db, Comment, Todo, COMMENTS_PER_TODO


class CommentTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=True)
        self.context = app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()
        self.todo = Todo(title='Private todo title')
        db.session.add(self.todo)
        db.session.commit()
        self.todo_id = self.todo.id
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        self.context.pop()

    def token(self, client=None, path='/'):
        response = (client or self.client).get(path)
        self.assertEqual(response.status_code, 200)
        return re.search(rb'name="csrf_token" value="([^"]+)"', response.data)[1].decode()

    def test_missing_invalid_and_other_session_tokens_are_rejected(self):
        other_session_token = self.token(app.test_client())
        for token in (None, 'invalid', other_session_token):
            with self.subTest(token_kind='missing' if token is None else 'invalid'):
                data = {'comment': 'Must not be saved'}
                if token is not None:
                    data['csrf_token'] = token
                response = self.client.post(f'/comment/{self.todo_id}', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(Comment.query.count(), 0)

    def test_valid_comment_is_saved_and_logs_only_event(self):
        token = self.token()
        with self.assertLogs(app.logger, level='INFO') as logs:
            response = self.client.post(
                f'/comment/{self.todo_id}',
                data={'comment': '  Private comment text  ', 'csrf_token': token},
                environ_overrides={'REMOTE_ADDR': '192.0.2.23'},
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual([record.getMessage() for record in logs.records], ['comment_created'])
        comment = Comment.query.one()
        self.assertEqual(comment.text, 'Private comment text')
        self.assertEqual(comment.todo_id, self.todo_id)
        self.assertIsNotNone(comment.created_at)
        self.assertIn(b'Private comment text', self.client.get('/').data)

    def test_blank_comment_is_not_saved(self):
        response = self.client.post(
            f'/comment/{self.todo_id}', data={'comment': '  ', 'csrf_token': self.token()}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.query.count(), 0)

    def test_database_failure_rolls_back_and_returns_error(self):
        token = self.token()
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError('private SQL')):
            with patch.object(db.session, 'rollback', wraps=db.session.rollback) as rollback:
                with self.assertLogs(app.logger, level='ERROR') as logs:
                    response = self.client.post(
                        f'/comment/{self.todo_id}',
                        data={'comment': 'Private text', 'csrf_token': token},
                    )
                rollback.assert_called_once_with()
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('Location', response.headers)
        self.assertIn(b'Unable to save your comment', response.data)
        self.assertNotIn(b'private SQL', response.data)
        self.assertEqual([record.getMessage() for record in logs.records], ['comment_save_failed'])
        self.assertEqual(Comment.query.count(), 0)
        response = self.client.post(
            f'/comment/{self.todo_id}', data={'comment': 'Retry', 'csrf_token': token}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.query.one().text, 'Retry')

    def test_unexpected_errors_are_not_swallowed(self):
        token = self.token()
        with patch.object(db.session, 'commit', side_effect=RuntimeError('programming error')):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    f'/comment/{self.todo_id}', data={'comment': 'text', 'csrf_token': token}
                )
        db.session.rollback()

    def test_comments_are_bulk_loaded_and_capped_per_todo(self):
        db.session.delete(self.todo)
        start = datetime(2026, 1, 1)
        for number in range(3):
            todo = Todo(title=f'Todo {number}', created_at=start + timedelta(days=number))
            db.session.add(todo)
            db.session.flush()
            # Insert in reverse timestamp order to check selection by recency, not ID.
            for position in reversed(range(COMMENTS_PER_TODO + 5)):
                db.session.add(Comment(
                    todo_id=todo.id, text=f'Comment {number}:{position}',
                    created_at=start + timedelta(minutes=position),
                ))
        db.session.commit()
        db.session.remove()
        statements = []

        def record_query(connection, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith('SELECT'):
                statements.append(statement)

        event.listen(db.engine, 'before_cursor_execute', record_query)
        try:
            response = self.client.get('/')
        finally:
            event.remove(db.engine, 'before_cursor_execute', record_query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(statements), 2)
        page = response.get_data(as_text=True)
        self.assertEqual(page.count('class="comment-item"'), 3 * COMMENTS_PER_TODO)
        self.assertLess(page.index('Todo 2'), page.index('Todo 1'))
        self.assertLess(page.index('Todo 1'), page.index('Todo 0'))
        for number in range(3):
            for position in range(COMMENTS_PER_TODO + 5):
                marker = f'Comment {number}:{position}</span>'
                if position < 5:
                    self.assertNotIn(marker, page)
                else:
                    self.assertIn(marker, page)
        self.assertEqual(Comment.query.count(), 3 * (COMMENTS_PER_TODO + 5))

    def test_empty_comment_collection_and_missing_todo(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        response = self.client.post(
            '/comment/999999', data={'comment': 'text', 'csrf_token': self.token()}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.query.count(), 0)

    def test_add_and_edit_forms_still_submit(self):
        response = self.client.post('/add', data={'title': 'New todo', 'csrf_token': self.token()})
        self.assertEqual(response.status_code, 302)
        new_todo = Todo.query.filter_by(title='New todo').one()
        path = f'/edit/{new_todo.id}'
        response = self.client.post(path, data={'title': 'Edited', 'csrf_token': self.token(path=path)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Todo, new_todo.id).title, 'Edited')

    def test_new_database_rejects_null_timestamp(self):
        with self.assertRaises(IntegrityError):
            db.session.execute(text(
                'INSERT INTO comment (todo_id, text, created_at) VALUES (:id, :text, NULL)'
            ), {'id': self.todo_id, 'text': 'Null timestamp'})
        db.session.rollback()


class MigrationTests(unittest.TestCase):
    def test_upgrade_backfills_nulls_preserves_data_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'legacy.db'
            with sqlite3.connect(database) as connection:
                connection.executescript('''
                    CREATE TABLE todo (
                        id INTEGER PRIMARY KEY, title VARCHAR(200) NOT NULL,
                        description TEXT, deadline DATETIME, completed BOOLEAN,
                        completed_at DATETIME, created_at DATETIME
                    );
                    CREATE TABLE comment (
                        id INTEGER PRIMARY KEY, todo_id INTEGER NOT NULL,
                        text TEXT NOT NULL, created_at DATETIME,
                        FOREIGN KEY(todo_id) REFERENCES todo(id)
                    );
                    CREATE INDEX legacy_comment_todo_id ON comment(todo_id);
                    INSERT INTO todo (id, title) VALUES (1, 'Preserved todo');
                    INSERT INTO comment VALUES (1, 1, 'Missing timestamp', NULL);
                    INSERT INTO comment VALUES (2, 1, 'Existing timestamp', '2020-01-02 03:04:05');
                ''')
            environment = dict(os.environ, DATABASE_URL=f'sqlite:///{database}')
            for _ in range(2):
                result = subprocess.run(
                    [sys.executable, '-m', 'alembic', 'upgrade', 'head'],
                    cwd=Path(__file__).resolve().parents[1], env=environment,
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with sqlite3.connect(database) as connection:
                rows = connection.execute('SELECT * FROM comment ORDER BY id').fetchall()
                self.assertEqual(rows[0][:3], (1, 1, 'Missing timestamp'))
                self.assertIsInstance(datetime.fromisoformat(rows[0][3]), datetime)
                self.assertEqual(rows[1], (2, 1, 'Existing timestamp', '2020-01-02 03:04:05'))
                self.assertEqual(connection.execute('SELECT title FROM todo').fetchone()[0],
                                 'Preserved todo')
                columns = connection.execute('PRAGMA table_info(comment)').fetchall()
                self.assertEqual(next(column for column in columns if column[1] == 'created_at')[3], 1)
                self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
                self.assertTrue(connection.execute('PRAGMA foreign_key_list(comment)').fetchall())
                indexes = connection.execute('PRAGMA index_list(comment)').fetchall()
                self.assertIn('legacy_comment_todo_id', [index[1] for index in indexes])
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute('INSERT INTO comment VALUES (3, 1, ?, NULL)', ('Invalid',))


if __name__ == '__main__':
    unittest.main()
