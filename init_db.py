from app import db, app
from app.models import User

with app.app_context():
    db.create_all()
    
    # Check if any user exists
    if not User.query.first():
        user = User(username="testuser", email="test@example.com", password="123456", profile_pic="default.jpg")
        db.session.add(user)
        db.session.commit()
        print("✅ Dummy user inserted.")
    else:
        print("⚠️ User already exists.")

    print("✅ Tables created successfully.")
