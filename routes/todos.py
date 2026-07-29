from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from models import db
from models.todo import Todo
from models.project import Project
from models.tag import Tag
from models.activity import ActivityLog

todos_bp = Blueprint('todos', __name__, url_prefix='/')


def get_today_date():
    """Return today's date as YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


def log_activity(action, entity_type, entity_id, entity_name, details=None):
    entry = ActivityLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        details=details
    )
    db.session.add(entry)


@todos_bp.route('/')
def index():
    project_id = request.args.get('project_id', type=int)
    tag_id = request.args.get('tag_id', type=int)

    query = Todo.query

    if project_id:
        query = query.filter_by(project_id=project_id)
    if tag_id:
        tag = Tag.query.get_or_404(tag_id)
        query = query.filter(Todo.tags.contains(tag))

    todos = query.order_by(Todo.created_at.desc()).all()
    projects = Project.query.order_by(Project.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    active_project = Project.query.get(project_id) if project_id else None
    active_tag = Tag.query.get(tag_id) if tag_id else None

    return render_template(
        'index.html',
        todos=todos,
        projects=projects,
        tags=tags,
        active_project=active_project,
        active_tag=active_tag,
        now=datetime.now()
    )


@todos_bp.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title', '').strip()
    if not title:
        return redirect(url_for('todos.index'))

    description = request.form.get('description', '').strip() or None
    deadline_str = request.form.get('deadline', '').strip()
    project_id = request.form.get('project_id', type=int)
    tag_ids = request.form.getlist('tag_ids', type=int)

    deadline_obj = None
    if deadline_str:
        try:
            deadline_obj = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass
    else:
        deadline_obj = datetime.strptime(get_today_date(), '%Y-%m-%d')

    new_todo = Todo(
        title=title,
        description=description,
        deadline=deadline_obj,
        project_id=project_id if project_id else None
    )

    if tag_ids:
        selected_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        new_todo.tags = selected_tags

    db.session.add(new_todo)
    db.session.flush()
    log_activity('created', 'todo', new_todo.id, new_todo.title)
    db.session.commit()

    return redirect(url_for('todos.index'))


@todos_bp.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    action = 'completed' if todo.completed else 'updated'
    log_activity(action, 'todo', todo.id, todo.title,
                 'Marked as completed' if todo.completed else 'Marked as incomplete')
    db.session.commit()
    return redirect(url_for('todos.index'))


@todos_bp.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    title = todo.title
    todo_id_val = todo.id
    db.session.delete(todo)
    log_activity('deleted', 'todo', todo_id_val, title)
    db.session.commit()
    return redirect(url_for('todos.index'))


@todos_bp.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    projects = Project.query.order_by(Project.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if title:
            todo.title = title
        todo.description = request.form.get('description', '').strip() or None
        deadline_str = request.form.get('deadline', '').strip()
        project_id = request.form.get('project_id', type=int)
        tag_ids = request.form.getlist('tag_ids', type=int)

        if deadline_str:
            try:
                todo.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        else:
            todo.deadline = None

        todo.project_id = project_id if project_id else None
        todo.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []

        log_activity('updated', 'todo', todo.id, todo.title)
        db.session.commit()
        return redirect(url_for('todos.index'))

    return render_template('edit.html', todo=todo, projects=projects, tags=tags)


@todos_bp.route('/bulk', methods=['POST'])
def bulk_action():
    action = request.form.get('action')
    project_id = request.form.get('project_id', type=int)

    query = Todo.query
    if project_id:
        query = query.filter_by(project_id=project_id)

    if action == 'complete_all':
        todos = query.filter_by(completed=False).all()
        for todo in todos:
            todo.completed = True
            log_activity('completed', 'todo', todo.id, todo.title, 'Bulk completed')
        db.session.commit()
    elif action == 'delete_completed':
        todos = query.filter_by(completed=True).all()
        for todo in todos:
            log_activity('deleted', 'todo', todo.id, todo.title, 'Bulk deleted')
            db.session.delete(todo)
        db.session.commit()

    if project_id:
        return redirect(url_for('todos.index', project_id=project_id))
    return redirect(url_for('todos.index'))
