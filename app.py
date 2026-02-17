from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key-change-in-production'

db = SQLAlchemy(app)

# Constants for validation
MAX_CATEGORY_LENGTH = 100

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    category = db.Column(db.String(100), default='General')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else None,
            'category': self.category,
            'completed': self.completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    incomplete_count = Todo.query.filter_by(completed=False).count()
    return render_template('index.html', todos=todos, incomplete_count=incomplete_count)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')
    category = request.form.get('category', '').strip() or 'General'

    if not title:
        flash('Title is required!', 'error')
        return redirect(url_for('index'))

    # Validate category length
    if len(category) > MAX_CATEGORY_LENGTH:
        flash(f'Category must be {MAX_CATEGORY_LENGTH} characters or less!', 'error')
        return redirect(url_for('index'))

    deadline_obj = None
    if deadline:
        try:
            deadline_obj = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid deadline format!', 'error')
            return redirect(url_for('index'))

    new_todo = Todo(title=title, description=description, deadline=deadline_obj, category=category)
    db.session.add(new_todo)
    db.session.commit()
    flash('Todo added successfully!', 'success')

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
        title = request.form.get('title', todo.title)
        description = request.form.get('description', todo.description)
        category = request.form.get('category', todo.category)
        deadline = request.form.get('deadline')

        # Validate title
        if not title:
            flash('Title is required!', 'error')
            return render_template('edit.html', todo=todo)

        # Validate category length
        if len(category) > MAX_CATEGORY_LENGTH:
            flash(f'Category must be {MAX_CATEGORY_LENGTH} characters or less!', 'error')
            return render_template('edit.html', todo=todo)

        # Update title, description, and category
        todo.title = title
        todo.description = description
        todo.category = category

        # Handle deadline
        if deadline:
            try:
                todo.deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid deadline format!', 'error')
                return render_template('edit.html', todo=todo)
        else:
            todo.deadline = None

        db.session.commit()
        flash('Todo updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', todo=todo)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
