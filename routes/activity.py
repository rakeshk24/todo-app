from flask import Blueprint, render_template
from models.activity import ActivityLog

activity_bp = Blueprint('activity', __name__, url_prefix='/activity')


@activity_bp.route('/')
def activity_log():
    entries = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(100).all()
    return render_template('activity.html', entries=entries)
