from werkzeug.security import generate_password_hash, check_password_hash

users_db = {}         # email: User object
friend_requests = {}  # receiver_email: [sender_email]
friendships = {}      # email: [friend_email list]

class User:
    def __init__(self, username, email, password, profile_pic):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.profile_pic = profile_pic

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# Existing part of models.py
from werkzeug.security import generate_password_hash, check_password_hash

users_db = {}         # email: User object
friend_requests = {}  # receiver_email: [sender_email]
friendships = {}      # email: [friend_email list]

class User:
    def __init__(self, username, email, password, profile_pic):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.profile_pic = profile_pic

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 📸 Posts structure
posts = []  # List of dicts: {email, image, caption, likes, comments}
