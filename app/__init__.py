from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///socialmedia.db'
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['PROFILE_FOLDER'] = 'app/static/avatars'
    app.config['STORY_FOLDER'] = 'app/static/stories'

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
