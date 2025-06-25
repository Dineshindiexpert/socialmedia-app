from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")  # Allow CORS for WebRTC signaling

def create_app():
    app = Flask(__name__, static_folder='static')

    # Basic config
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Import routes after app init to avoid circular import
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
