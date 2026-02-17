# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application for managing a todo list. It provides CRUD operations for todos with optional features like deadlines, descriptions, and categories. The app uses SQLite for persistent storage via SQLAlchemy ORM.

## Architecture

The application follows a simple MVC-like structure:

- **Backend (app.py)**: Flask application with SQLAlchemy database model and all route handlers
  - Single `Todo` database model with fields: id, title, description, deadline, category, completed, created_at
  - Routes for listing, adding, editing, deleting, and toggling completion status
  - Form validation for required fields (title) and field length constraints (category max 100 chars)
  - Deadline parsing with error handling for datetime-local format conversion

- **Frontend**: Jinja2 templates with custom CSS
  - `templates/index.html`: Main page displaying the todo list form and all todos with action buttons
  - `static/style.css`: Responsive design with gradient background, modern component styling, and mobile breakpoint at 600px
  - Flash messages for success/error feedback

- **Database**: SQLite (file-based, auto-created at `instance/todos.db`)
  - No schema migrations needed; `db.create_all()` runs on app startup

## Development Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run the application**: `python app.py` (starts dev server on http://localhost:5001)
- **Reset database**: Delete `instance/todos.db` and restart the app

## Key Implementation Details

### Form Handling
All form submissions use traditional POST requests with page redirects. The app uses Flask's `flash()` for displaying validation errors and success messages.

### Validation
- **Title**: Required field, validated on both add and edit routes (app.py:55, 104)
- **Category**: Maximum 100 characters enforced (app.py:60, 109)
- **Deadline**: Parsed from HTML5 datetime-local format (`YYYY-MM-DDTHH:MM`). Invalid dates show error flash message (app.py:66-70, 120-124)

### Database State Management
- Todos are ordered by `created_at` descending on the index page (app.py:44)
- Incomplete count is calculated on each page load (app.py:45)
- All database operations use SQLAlchemy session management with explicit commits

### Frontend Interaction
- Checkbox toggling and deletions use traditional links (GET requests), not AJAX
- Delete action includes JavaScript confirmation dialog (templates/index.html:96)
- Completed todos display with strike-through styling and reduced opacity (static/style.css:233-242)

## Dependencies

- **Flask 2.3.3**: Web framework
- **Flask-SQLAlchemy 3.0.5**: ORM integration
- **SQLAlchemy 2.0.21**: Database ORM
- **Werkzeug 2.3.7**: WSGI utilities

## Configuration

- **Debug mode**: Enabled by default in app.py:135 (development only)
- **Port**: 5001 (app.py:135)
- **Secret key**: Placeholder value in app.py:9—must be changed before production deployment

## Notes for Future Development

- The app uses traditional server-side form submissions rather than AJAX, making it suitable for simple deployments
- CSS is embedded in a single file with utility classes for buttons (btn-primary, btn-edit, btn-delete)
- No JavaScript dependencies beyond HTML5 native validation
- Consider implementing pagination if todo count grows significantly
