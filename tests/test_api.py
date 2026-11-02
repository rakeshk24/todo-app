import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch


# Load an isolated copy so the tests cannot alter a developer's SQLite database.
ROOT = Path(__file__).resolve().parents[1]
TEMP = tempfile.TemporaryDirectory()
APP_ROOT = Path(TEMP.name)
shutil.copy(ROOT / 'app.py', APP_ROOT / 'app.py')
shutil.copytree(ROOT / 'templates', APP_ROOT / 'templates')
shutil.copytree(ROOT / 'static', APP_ROOT / 'static')
TEST_ENV = os.environ.copy()
TEST_ENV['TODO_API_KEY'] = 'test-key-only'
TEST_ENV.pop('TRUSTED_PROXY_HOPS', None)
TEST_ENV.pop('ALLOW_INSECURE_HTTP', None)
spec = importlib.util.spec_from_file_location('todo_app_test', APP_ROOT / 'app.py')
todo_app = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = todo_app
with patch.dict(os.environ, TEST_ENV, clear=True):
    spec.loader.exec_module(todo_app)


def tearDownModule():
    sys.modules.pop(spec.name, None)
    TEMP.cleanup()


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = todo_app.app.test_client()
        self.headers = {'X-API-Key': 'test-key-only'}
        self.https = 'https://example.test'
        with todo_app.app.app_context():
            todo_app.db.session.query(todo_app.Todo).delete()
            todo_app.db.session.commit()

    def test_secret_is_required_and_key_is_checked(self):
        env = TEST_ENV.copy()
        env.pop('TODO_API_KEY')
        result = subprocess.run([sys.executable, str(APP_ROOT / 'app.py')], env=env,
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('TODO_API_KEY must be configured', result.stderr)
        self.assertEqual(self.client.get('/api/todos', base_url=self.https).status_code, 401)
        self.assertEqual(self.client.get('/api/todos', base_url=self.https,
                                         headers=self.headers).status_code, 200)

    def test_pagination_limits_and_orders_selected_page(self):
        with todo_app.app.app_context():
            now = datetime(2024, 1, 1)
            todo_app.db.session.add_all([
                todo_app.Todo(title=str(i), description='', created_at=now + timedelta(minutes=i))
                for i in range(105)
            ])
            todo_app.db.session.commit()
        response = self.client.get('/api/todos?page=2&per_page=3', base_url=self.https,
                                   headers=self.headers)
        self.assertEqual([item['title'] for item in response.json], ['101', '100', '99'])
        self.assertEqual(len(self.client.get('/api/todos', base_url=self.https,
                                             headers=self.headers).json), 20)
        self.assertEqual(len(self.client.get('/api/todos?per_page=100', base_url=self.https,
                                             headers=self.headers).json), 100)
        for query in ('page=0', 'page=-1', 'page=abc', 'per_page=101', 'per_page=0',
                      'page=' + '9' * 5000):
            with self.subTest(query=query[:30]):
                self.assertEqual(self.client.get('/api/todos?' + query, base_url=self.https,
                                                 headers=self.headers).status_code, 400)

    def test_json_validation_and_deadline(self):
        for data in ([], None, 'text', {}, {'title': 'x'}, {'title': 1, 'description': ''},
                     {'title': 'x', 'description': []}, {'title': '', 'description': ''}):
            with self.subTest(data=data):
                response = self.client.post('/api/todos', json=data, base_url=self.https,
                                            headers=self.headers)
                self.assertEqual(response.status_code, 400)
                self.assertTrue(response.is_json)
        for deadline in ('tomorrow', '2024-02-30T12:30', 42, []):
            response = self.client.post('/api/todos', base_url=self.https, headers=self.headers,
                                        json={'title': 'x', 'description': '', 'deadline': deadline})
            self.assertEqual(response.status_code, 400)
        for deadline in (None, '', '2024-02-29T12:30'):
            response = self.client.post('/api/todos', base_url=self.https, headers=self.headers,
                                        json={'title': 'x', 'description': '', 'deadline': deadline})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['deadline'], '2024-02-29 12:30' if deadline else None)
        response = self.client.post('/api/todos', base_url=self.https, headers=self.headers,
                                    json={'title': 'x', 'description': ''})
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json['deadline'])

    def test_missing_todo_is_json(self):
        response = self.client.get('/api/todos/999999', base_url=self.https, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'error': 'Todo not found'})

    def test_https_and_example_urls(self):
        response = self.client.get('/', headers={'X-Forwarded-Proto': 'https'})
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/', base_url=self.https)
        self.assertEqual(response.status_code, 200)
        self.assertIn('max-age=', response.headers['Strict-Transport-Security'])
        self.assertIn(b'https://your-domain.example/api/todos', response.data)
        self.assertNotIn(b'http://example.test/api/todos', response.data)

    def test_trusted_proxy_configuration(self):
        env = TEST_ENV.copy()
        env['TRUSTED_PROXY_HOPS'] = '1'
        script = ("import app; c=app.app.test_client(); "
                  "assert c.get('/').status_code == 400; "
                  "r=c.get('/', headers={'X-Forwarded-Proto':'https'}); "
                  "assert r.status_code == 200 and 'Strict-Transport-Security' in r.headers")
        result = subprocess.run([sys.executable, '-c', script], cwd=APP_ROOT, env=env,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_note_contrast(self):
        def luminance(hex_color):
            values = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                      for v in values]
            return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))
        css = (APP_ROOT / 'static/style.css').read_text()
        self.assertIn('color: #555;', css.split('.api-note {', 1)[1].split('}', 1)[0])
        self.assertIn('background: #f8f9fa;',
                      css.split('.api-info-section {', 1)[1].split('}', 1)[0])
        self.assertGreaterEqual((luminance('f8f9fa') + 0.05) / (luminance('555555') + 0.05), 4.5)


if __name__ == '__main__':
    unittest.main()
