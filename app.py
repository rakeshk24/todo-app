from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
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

class SubTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subtasks = db.relationship('SubTask', backref='todo', lazy='select', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else None,
            'completed': self.completed,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    todos = Todo.query.options(joinedload(Todo.subtasks)).order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/subtask/add', methods=['POST'])
def add_subtask():
    todo_id = request.form.get('todo_id', type=int)
    text = request.form.get('text', '').strip()
    if not text or not todo_id:
        return redirect(url_for('index'))
    todo = Todo.query.get_or_404(todo_id)
    subtask = SubTask(todo_id=todo.id, text=text)
    db.session.add(subtask)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/subtask/toggle/<int:subtask_id>')
def toggle_subtask(subtask_id):
    subtask = SubTask.query.get_or_404(subtask_id)
    todo = Todo.query.get(subtask.todo_id)
    print(f"Subtask '{subtask.text}' toggled on '{todo.title}' by {request.remote_addr}")
    subtask.completed = not subtask.completed
    db.session.commit()
    return redirect(url_for('index'))

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
