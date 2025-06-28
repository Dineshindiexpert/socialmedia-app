import os
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager, socketio
from app.models import User
from flask_socketio import emit

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        profile = request.files.get('profile')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
        else:
            filename = secure_filename(profile.filename)
            profile_path = os.path.join(app.static_folder, 'uploads', filename)
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)
            profile.save(profile_path)

            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                profile_pic=filename
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Registration successful. Welcome!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/call')
@login_required
def call():
    return render_template('call.html')

# SocketIO Events
@socketio.on('video-offer')
def handle_offer(data):
    emit('video-offer', data, broadcast=True, include_self=False)

@socketio.on('video-answer')
def handle_answer(data):
    emit('video-answer', data, broadcast=True, include_self=False)

@socketio.on('ice-candidate')
def handle_ice(data):
    emit('ice-candidate', data, broadcast=True, include_self=False)

@socketio.on('end-call')
def handle_end():
    emit('end-call', broadcast=True, include_self=False)
