from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Post
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

# ✅ Home Page Route
@main.route('/')
def home():
    return render_template('index.html')

# ✅ Login Route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# ✅ Register Route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registered successfully.")
            return redirect(url_for('main.login'))
    return render_template('register.html')

# ✅ Dashboard Route
@main.route('/dashboard')
@login_required
def dashboard():
    posts = Post.query.all()
    return render_template('dashboard.html', posts=posts)

# ✅ Upload Post Route
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_post():
    if request.method == 'POST':
        caption = request.form['caption']
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join('app/static/uploads', filename)
            file.save(filepath)
            new_post = Post(user_id=current_user.id, image=filename, caption=caption)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
    return render_template('upload_post.html')

# ✅ Call Page
@main.route('/call')
@login_required
def call():
    return render_template('call.html')

# ✅ Chat Page
@main.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# ✅ Profile Page
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# ✅ Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
