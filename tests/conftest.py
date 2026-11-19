import os
import pytest

os.environ.setdefault('ALLOW_INSECURE_HTTP', '1')

from app import app as flask_app, db


@pytest.fixture(scope='session')
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'ALLOW_INSECURE_HTTP': True,
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        db.create_all()
    yield flask_app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    yield
