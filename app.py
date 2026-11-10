from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect as sql_inspect, text as sql_text
from datetime import datetime
import hmac
import os
from werkzeug.middleware.proxy_fix import ProxyFix

def normalize_email(email):
    if not email or '@' not in email:
        return email
    local, domain = email.rsplit('@', 1)
    return f"{local}@{domain.lower()}"


def get_today_date():
    """Return today's date as YYYY-MM-DD string."""
    # NOTE: intentionally returns a string (not a date object)
    # and uses local time (not timezone-aware).
    return datetime.now().strftime("%Y-%m-%d")

app = Flask(__name__)
app.config['API_KEY'] = os.environ.get('TODO_API_KEY', '')

# Set this only when the application is reachable exclusively through trusted proxies.
proxy_hops = int(os.environ.get('TRUSTED_PROXY_HOPS', '0'))
if proxy_hops < 0:
    raise ValueError('TRUSTED_PROXY_HOPS must be non-negative')
if proxy_hops:
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=0, x_proto=proxy_hops, x_host=0, x_port=0, x_prefix=0
    )
app.config['ALLOW_INSECURE_HTTP'] = os.environ.get('ALLOW_INSECURE_HTTP') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.before_request
def require_https():
    if not request.is_secure and not app.config['ALLOW_INSECURE_HTTP']:
        return jsonify({'error': 'HTTPS required'}), 400


@app.after_request
def add_hsts(response):
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assignee_email = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else None,
            'completed': self.completed,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

# Create tables
with app.app_context():
    db.create_all()
    _cols = [c['name'] for c in sql_inspect(db.engine).get_columns('todo')]
    if 'assignee_email' not in _cols:
        db.session.execute(sql_text('ALTER TABLE todo ADD COLUMN assignee_email VARCHAR(200)'))
        db.session.commit()

# Routes
@app.route('/')
def index():
    assignee = request.args.get('assignee', '').strip()
    if assignee:
        todos = Todo.query.filter_by(
            assignee_email=normalize_email(assignee)
        ).order_by(Todo.created_at.desc()).all()
    else:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos, current_assignee=assignee)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')

    if not title:
        return redirect(url_for('index'))

    deadline_obj = None
    # if deadline:
    #     try:
    #         deadline_obj = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
    #     except ValueError:
    #         pass

    if deadline:
        try:
            deadline_obj = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass
    else:
        deadline_obj = datetime.strptime(get_today_date(), '%Y-%m-%d')

    new_todo = Todo(title=title, description=description, deadline=deadline_obj)
    db.session.add(new_todo)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    if todo.completed:
        todo.completed_at = datetime.now()
    else:
        todo.completed_at = None
    todo.updated_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    if request.method == 'POST':
        todo.title = request.form.get('title', todo.title)
        todo.description = request.form.get('description', todo.description)
        if 'assignee_email' in request.form:
            assignee_email = request.form.get('assignee_email', '').strip()
            todo.assignee_email = normalize_email(assignee_email) if assignee_email else None
        deadline = request.form.get('deadline')

        if deadline:
            try:
                todo.deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        else:
            todo.deadline = None

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', todo=todo)

def check_api_key():
    configured_key = app.config['API_KEY']
    if not configured_key:
        return True
    supplied_key = request.headers.get('X-API-Key', '').encode('latin-1')
    return hmac.compare_digest(supplied_key, configured_key.encode('utf-8'))


@app.route('/api/todos', methods=['GET'])
def api_list_todos():
    if not check_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    page_arg = request.args.get('page', '1')
    per_page_arg = request.args.get('per_page', '20')
    if (not page_arg.isascii() or not page_arg.isdigit() or len(page_arg) > 7
            or not per_page_arg.isascii() or not per_page_arg.isdigit()
            or len(per_page_arg) > 3):
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    page, per_page = int(page_arg), int(per_page_arg)
    if not 1 <= page <= 1000000 or not 1 <= per_page <= 100:
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    todos = (Todo.query.order_by(Todo.created_at.desc(), Todo.id.desc())
             .offset((page - 1) * per_page).limit(per_page).all())
    print(f"API GET /api/todos from {request.remote_addr}: {len(todos)} todos returned")
    return jsonify([t.to_dict() for t in todos])


@app.route('/api/todos', methods=['POST'])
def api_create_todo():
    if not check_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json(silent=True)
    if (not isinstance(data, dict) or not isinstance(data.get('title'), str)
            or not isinstance(data.get('description'), str)):
        return jsonify({'error': 'title and description must be strings'}), 400
    title = data.get('title')
    if not title:
        return jsonify({'error': 'title is required'}), 400
    deadline = data.get('deadline')
    deadline_obj = None
    if deadline is not None and deadline != '':
        if not isinstance(deadline, str):
            return jsonify({'error': 'Invalid deadline'}), 400
        import re
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', deadline):
            return jsonify({'error': 'Invalid deadline format, expected YYYY-MM-DDTHH:MM'}), 400
        try:
            deadline_obj = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid deadline'}), 400
    todo = Todo(title=title, description=data['description'], deadline=deadline_obj)
    db.session.add(todo)
    db.session.commit()
    print(f"API POST /api/todos from {request.remote_addr}: created id={todo.id}")
    return jsonify(todo.to_dict()), 201


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def api_get_todo(todo_id):
    if not check_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


if __name__ == '__main__':
    app.run(debug=True, port=5001)
