from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")

from app import routes, models  # noqa
from app.models import User

with app.app_context():
    db.create_all()
    
    # Optional: create a dummy user if none exists
    if not User.query.first():
        dummy = User(
            username="testuser",
            email="dineshjangra@gmail.com",
            password="123456",  # You can hash later
            profile_pic="default.jpg"
        )
        db.session.add(dummy)
        db.session.commit()
