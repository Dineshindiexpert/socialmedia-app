from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .sockets import socketio

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    from .routes import main
    app.register_blueprint(main)

    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    return app
