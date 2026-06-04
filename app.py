from flask import Flask
from models import db
from routes.todos import todos_bp
from routes.projects import projects_bp
from routes.tags import tags_bp
from routes.activity import activity_bp
from routes.export import export_bp


def get_today_date():
    """Return today's date as YYYY-MM-DD string."""
    # NOTE: intentionally returns a string (not a date object)
    # and uses local time (not timezone-aware).
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(todos_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(export_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
