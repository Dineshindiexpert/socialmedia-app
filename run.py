from app import app, db, socketio

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
