from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import db
from models.tag import Tag
from models.activity import ActivityLog

tags_bp = Blueprint('tags', __name__, url_prefix='/tags')


def log_activity(action, entity_type, entity_id, entity_name, details=None):
    entry = ActivityLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        details=details
    )
    db.session.add(entry)


@tags_bp.route('/')
def list_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags.html', tags=tags)


@tags_bp.route('/add', methods=['POST'])
def add_tag():
    name = request.form.get('name', '').strip()
    if not name:
        return redirect(url_for('tags.list_tags'))

    color = request.form.get('color', '#28a745').strip() or '#28a745'

    # Check for duplicate name
    existing = Tag.query.filter_by(name=name).first()
    if existing:
        return redirect(url_for('tags.list_tags'))

    tag = Tag(name=name, color=color)
    db.session.add(tag)
    db.session.flush()
    log_activity('created', 'tag', tag.id, tag.name)
    db.session.commit()

    return redirect(url_for('tags.list_tags'))


@tags_bp.route('/<int:tag_id>/delete')
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    name = tag.name
    tid = tag.id
    db.session.delete(tag)
    log_activity('deleted', 'tag', tid, name)
    db.session.commit()
    return redirect(url_for('tags.list_tags'))


@tags_bp.route('/api/all')
def api_all_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([{'id': t.id, 'name': t.name, 'color': t.color} for t in tags])
