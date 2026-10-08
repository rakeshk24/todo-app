from alembic import context

from app import app, db


with app.app_context():
    with db.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=db.metadata)
        with context.begin_transaction():
            context.run_migrations()
