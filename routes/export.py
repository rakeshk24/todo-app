import csv
import io
import json
from datetime import datetime
from flask import Blueprint, Response
from models.todo import Todo

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/csv')
def export_csv():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'description', 'deadline', 'completed', 'project', 'tags', 'created_at'])

    for todo in todos:
        writer.writerow([
            todo.title,
            todo.description or '',
            todo.deadline.strftime('%Y-%m-%d %H:%M') if todo.deadline else '',
            todo.completed,
            todo.project.name if todo.project else '',
            ', '.join(t.name for t in todo.tags),
            todo.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@export_bp.route('/json')
def export_json():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()

    data = []
    for todo in todos:
        data.append({
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'deadline': todo.deadline.strftime('%Y-%m-%d %H:%M') if todo.deadline else None,
            'completed': todo.completed,
            'project': todo.project.name if todo.project else None,
            'tags': [t.name for t in todo.tags],
            'created_at': todo.created_at.strftime('%Y-%m-%d %H:%M')
        })

    json_data = json.dumps(data, indent=2)
    filename = f"todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        json_data,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
