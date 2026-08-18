from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
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

todo_tags = db.Table(
    'todo_tags',
    db.Column('todo_id', db.Integer, db.ForeignKey('todo.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('Tag', secondary=todo_tags, backref='todos', lazy='subquery')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else None,
            'completed': self.completed,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'tags': [t.name for t in self.tags],
        }

# Create tables
with app.app_context():
    db.create_all()

def _parse_tags(raw):
    """Return a deduplicated list of stripped, non-empty tag names from a comma-separated string."""
    seen = set()
    result = []
    for t in raw.split(','):
        name = t.strip()
        if name and name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _get_or_create_tags(names):
    if not names:
        return []
    existing = Tag.query.filter(Tag.name.in_(names)).all()
    existing_by_name = {t.name: t for t in existing}
    tags = []
    for name in names:
        if name in existing_by_name:
            tags.append(existing_by_name[name])
        else:
            tag = Tag(name=name)
            db.session.add(tag)
            existing_by_name[name] = tag
            tags.append(tag)
    return tags


# Routes
@app.route('/')
def index():
    tag_filter = request.args.get('tag', '').strip()
    all_tags = Tag.query.order_by(Tag.name).all()

    if tag_filter:
        todos = (
            Todo.query
            .join(Todo.tags)
            .filter(Tag.name == tag_filter)
            .order_by(Todo.created_at.desc())
            .all()
        )
    else:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()

    return render_template('index.html', todos=todos, all_tags=all_tags, active_tag=tag_filter)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')
    raw_tags = request.form.get('tags', '')

    if not title:
        return redirect(url_for('index'))

    deadline_obj = None
    if deadline:
        try:
            deadline_obj = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass
    else:
        deadline_obj = datetime.strptime(get_today_date(), '%Y-%m-%d')

    new_todo = Todo(title=title, description=description, deadline=deadline_obj)
    new_todo.tags = _get_or_create_tags(_parse_tags(raw_tags))
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
        raw_tags = request.form.get('tags', '')

        if deadline:
            try:
                todo.deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        else:
            todo.deadline = None

        todo.tags = _get_or_create_tags(_parse_tags(raw_tags))
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', todo=todo)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
