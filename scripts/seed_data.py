"""Seed the database with sample todos for development."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('ALLOW_INSECURE_HTTP', '1')

from app import app, db, Todo
from datetime import datetime, timedelta

SEED_TODOS = [
    {
        'title': 'Set up project structure',
        'priority': 'high',
        'description': 'Initialize repo and configure the development environment',
        'assignee_email': 'dev@example.com',
    },
    {
        'title': 'Write unit tests',
        'priority': 'medium',
        'description': 'Cover all routes, models, and utility functions',
        'deadline': datetime.now() + timedelta(days=7),
    },
    {
        'title': 'Update documentation',
        'priority': 'low',
        'description': 'README, API docs, and contributing guide',
    },
    {
        'title': 'Code review open PRs',
        'priority': 'high',
        'description': 'Review all open pull requests before the sprint ends',
        'assignee_email': 'reviewer@example.com',
        'deadline': datetime.now() + timedelta(days=2),
    },
    {
        'title': 'Deploy to staging',
        'priority': 'medium',
        'description': 'Push latest changes to Vercel staging environment',
        'deadline': datetime.now() + timedelta(days=3),
    },
    {
        'title': 'Monitor production logs',
        'priority': 'low',
        'description': 'Check for errors after the last deployment',
        'completed': True,
    },
    {
        'title': 'Upgrade dependencies',
        'priority': 'low',
        'description': 'Run renovate and review dependency updates',
    },
    {
        'title': 'Fix flaky test in CI',
        'priority': 'medium',
        'description': 'test_toggle_todo fails intermittently on main',
        'assignee_email': 'qa@example.com',
    },
]


def run():
    with app.app_context():
        db.create_all()
        existing = Todo.query.count()
        if existing > 0:
            print(f"Database already has {existing} todos — skipping seed.")
            return
        for data in SEED_TODOS:
            todo = Todo(**data)
            db.session.add(todo)
        db.session.commit()
        print(f"Seeded {len(SEED_TODOS)} todos successfully.")


if __name__ == '__main__':
    run()
