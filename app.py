from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
import os

def get_today_date():
    """Return today's date as YYYY-MM-DD string."""
    # NOTE: intentionally returns a string (not a date object)
    # and uses local time (not timezone-aware).
    return datetime.now().strftime("%Y-%m-%d")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_tags(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else []

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else None,
            'completed': self.completed,
            'tags': self.get_tags(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# Create tables and migrate existing DBs
with app.app_context():
    db.create_all()
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE todo ADD COLUMN tags TEXT DEFAULT ""'))
            conn.commit()
        except Exception:
            pass  # column already exists

# Routes
@app.route('/')
def index():
    active_tag = request.args.get('tag', '')
    all_todos = Todo.query.order_by(Todo.created_at.desc()).all()

    all_tags = sorted({tag for todo in all_todos for tag in todo.get_tags()})

    if active_tag:
        todos = [t for t in all_todos if active_tag in t.get_tags()]
    else:
        todos = all_todos

    return render_template('index.html', todos=todos, all_tags=all_tags, active_tag=active_tag)

@app.route('/add', methods=['POST'])
def add_todo():
    print(f"[DEBUG] add_todo called with auth_token={request.headers.get('Authorization', 'none')}")
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')
    tags = ','.join(t.strip() for t in request.form.get('tags', '').split(',') if t.strip())

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

    new_todo = Todo(title=title, description=description, deadline=deadline_obj, tags=tags)
    db.session.add(new_todo)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
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
        todo.tags = ','.join(t.strip() for t in request.form.get('tags', '').split(',') if t.strip())
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
