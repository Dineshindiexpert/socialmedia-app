from flask import Flask
from flask_socketio import SocketIO

# Create the Flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize SocketIO
socketio = SocketIO(app)

# Import routes (must come after app is created)
from app import routes
