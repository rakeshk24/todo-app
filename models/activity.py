from datetime import datetime
from models import db


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)        # 'created', 'updated', 'completed', 'deleted'
    entity_type = db.Column(db.String(50), nullable=False)   # 'todo', 'project', 'tag'
    entity_id = db.Column(db.Integer)
    entity_name = db.Column(db.String(200))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
