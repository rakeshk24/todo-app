# Todo List Web App

A simple and elegant web-based todo list application built with Python Flask.

## Features

- ✅ **CRUD Operations**: Create, read, update, and delete todos
- 📋 **Todo List**: View all your todos in an organized list
- ⏰ **Deadlines**: Add optional deadlines to your todos
- ✔️ **Completion Tracking**: Mark todos as done with a checkbox
- 📝 **Descriptions**: Add detailed descriptions to your todos
- 🎨 **Modern UI**: Clean and responsive design

## Project Structure

```
sample/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── static/
│   └── style.css      # CSS styling
└── templates/
    ├── index.html     # Main todo list page
    └── edit.html      # Edit todo page
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd sample
pip install -r requirements.txt
```

### 2. Run the Application

Set a stable, random `SECRET_KEY` environment variable for deployed instances so
CSRF tokens remain valid across workers and restarts. Local development falls back
to a random key that lasts for the process lifetime.

```bash
alembic upgrade head
python app.py
```

The app will be available at `http://localhost:5000`

## Usage

### Add a Todo
1. Enter a title (required)
2. Optionally add a description
3. Optionally set a deadline
4. Click "Add Todo"

### Toggle Completion
- Click the checkbox next to a todo to mark it as done/undone

### Edit a Todo
- Click the "Edit" button on any todo to modify it

### Delete a Todo
- Click the "Delete" button to remove a todo

## Database

The app uses SQLite for persistent storage. The database file (`todos.db`) is automatically created when you first run the app.

Before deploying an update, back up `instance/todos.db`, stop application writers,
and run `alembic upgrade head` from the repository root. The first migration fills
missing comment timestamps with the migration time (UTC), then enforces NOT NULL
while preserving existing timestamps and comments. `db.create_all()` alone does
not upgrade existing tables. `DATABASE_URL` can override the default database URL;
use the same value for migration and application commands.

Each todo displays its 50 most recent comments, with older comments retained in
the database. The todo list itself keeps its existing ordering and size.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests use a temporary SQLite database and keep CSRF protection enabled.

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3
- **Styling**: Responsive CSS with gradient design

## Notes

- The app uses SQLite which is file-based and requires no additional setup
- All todos are saved to the database automatically
- The app includes form validation and error handling
