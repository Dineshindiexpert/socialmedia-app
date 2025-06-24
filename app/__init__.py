from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'  # endpoint name for @login_required redirect
login_manager.login_message_category = 'info'
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    # You should set SECRET_KEY via env var or config file in production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
    # For SQLite:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    # Folder to save uploads:
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Import routes after initializing app to avoid circular imports
    from app import routes
    # No blueprint in this example; routes are registered directly.

    # If first time, create tables:
    with app.app_context():
        db.create_all()

    return app
