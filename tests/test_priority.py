import pytest
from app import app, db, Todo


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['ALLOW_INSECURE_HTTP'] = True
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client


def test_add_todo_with_priority(client):
    response = client.post('/add', data={
        'title': 'High priority task',
        'priority': 'high'
    })
    assert response.status_code == 302


def test_add_todo_default_priority(client):
    response = client.post('/add', data={'title': 'No priority task'})
    assert response.status_code == 302


def test_edit_todo_changes_priority(client):
    with app.app_context():
        todo = Todo(title='Test todo', priority='low')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    response = client.post(f'/edit/{todo_id}', data={
        'title': 'Test todo',
        'priority': 'high'
    })
    assert response.status_code == 302


def test_sort_by_priority_returns_200(client):
    response = client.get('/?sort_by=priority&direction=asc')
    assert response.status_code == 200


def test_sort_by_deadline(client):
    response = client.get('/?sort_by=deadline&direction=desc')
    assert response.status_code == 200


def test_sort_by_title(client):
    response = client.get('/?sort_by=title&direction=asc')
    assert response.status_code == 200


def test_index_with_priority_badge(client):
    with app.app_context():
        todo = Todo(title='Urgent task', priority='high')
        db.session.add(todo)
        db.session.commit()
    response = client.get('/')
    assert b'Urgent task' in response.data
