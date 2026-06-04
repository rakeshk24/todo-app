from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from models import db
from models.project import Project
from models.todo import Todo
from models.activity import ActivityLog

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


def log_activity(action, entity_type, entity_id, entity_name, details=None):
    entry = ActivityLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        details=details
    )
    db.session.add(entry)


@projects_bp.route('/')
def list_projects():
    projects = Project.query.order_by(Project.name).all()
    return render_template('projects.html', projects=projects)


@projects_bp.route('/add', methods=['POST'])
def add_project():
    name = request.form.get('name', '').strip()
    if not name:
        return redirect(url_for('projects.list_projects'))

    description = request.form.get('description', '').strip() or None
    color = request.form.get('color', '#667eea').strip() or '#667eea'

    project = Project(name=name, description=description, color=color)
    db.session.add(project)
    db.session.flush()
    log_activity('created', 'project', project.id, project.name)
    db.session.commit()

    return redirect(url_for('projects.list_projects'))


@projects_bp.route('/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    todos = Todo.query.filter_by(project_id=project_id).order_by(Todo.created_at.desc()).all()
    return render_template('project_detail.html', project=project, todos=todos, now=datetime.now())


@projects_bp.route('/<int:project_id>/edit', methods=['POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    name = request.form.get('name', '').strip()
    if name:
        project.name = name
    project.description = request.form.get('description', '').strip() or None
    color = request.form.get('color', '').strip()
    if color:
        project.color = color

    log_activity('updated', 'project', project.id, project.name)
    db.session.commit()
    return redirect(url_for('projects.list_projects'))


@projects_bp.route('/<int:project_id>/delete')
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    name = project.name
    pid = project.id

    # Disassociate todos from this project
    Todo.query.filter_by(project_id=project_id).update({'project_id': None})

    db.session.delete(project)
    log_activity('deleted', 'project', pid, name)
    db.session.commit()
    return redirect(url_for('projects.list_projects'))
