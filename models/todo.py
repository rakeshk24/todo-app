from datetime import datetime
from models import db
from models.tag import todo_tags


class Todo(db.Model):
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

    tags = db.relationship('Tag', secondary=todo_tags, backref=db.backref('todos', lazy=True), lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else None,
            'completed': self.completed,
            'project': self.project.name if self.project else None,
            'tags': [t.name for t in self.tags],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }
