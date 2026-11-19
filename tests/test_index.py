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
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


def test_index_shows_no_todos_placeholder(client):
    response = client.get('/')
    assert b'No todos yet' in response.data


def test_index_shows_added_todo(client):
    client.post('/add', data={'title': 'Walk the dog', 'priority': 'low'})
    response = client.get('/')
    assert b'Walk the dog' in response.data


def test_index_high_priority_todo_first_in_default_sort(client):
    with app.app_context():
        db.session.add(Todo(title='Low task', priority='low'))
        db.session.add(Todo(title='High task', priority='high'))
        db.session.commit()
    response = client.get('/?sort_by=priority&direction=asc')
    assert response.status_code == 200
    content = response.data.decode()
    high_pos = content.find('High task')
    low_pos = content.find('Low task')
    assert high_pos < low_pos


def test_index_sort_by_title_asc(client):
    with app.app_context():
        db.session.add(Todo(title='Zebra task', priority='none'))
        db.session.add(Todo(title='Apple task', priority='none'))
        db.session.commit()
    response = client.get('/?sort_by=title&direction=asc')
    content = response.data.decode()
    apple_pos = content.find('Apple task')
    zebra_pos = content.find('Zebra task')
    assert apple_pos < zebra_pos


def test_index_filter_by_assignee(client):
    with app.app_context():
        db.session.add(Todo(title='Assigned task', assignee_email='alice@example.com'))
        db.session.add(Todo(title='Unassigned task'))
        db.session.commit()
    response = client.get('/?assignee=alice@example.com')
    assert b'Assigned task' in response.data
    assert b'Unassigned task' not in response.data


def test_add_todo_missing_title_redirects(client):
    response = client.post('/add', data={'title': ''})
    assert response.status_code == 302


def test_add_todo_with_all_fields(client):
    response = client.post('/add', data={
        'title': 'Full task',
        'description': 'With description',
        'priority': 'high',
        'assignee_email': 'bob@example.com'
    })
    assert response.status_code == 302
    with app.app_context():
        todo = Todo.query.filter_by(title='Full task').first()
        assert todo is not None
        assert todo.priority == 'high'


def test_toggle_todo(client):
    with app.app_context():
        todo = Todo(title='Toggle me', priority='none')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    response = client.get(f'/toggle/{todo_id}')
    assert response.status_code == 302
    with app.app_context():
        updated = db.session.get(Todo, todo_id)
        assert updated.completed is True


def test_delete_todo(client):
    with app.app_context():
        todo = Todo(title='Delete me', priority='none')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    client.get(f'/delete/{todo_id}')
    with app.app_context():
        assert db.session.get(Todo, todo_id) is None
