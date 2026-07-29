from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.todo import Todo
from models.project import Project
from models.tag import Tag, todo_tags
from models.activity import ActivityLog

__all__ = ['db', 'Todo', 'Project', 'Tag', 'todo_tags', 'ActivityLog']
