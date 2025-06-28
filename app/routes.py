from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
import os

from app import app, db, login_manager, socketio
from app.models import User
from flask_socketio import emit

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        profile = request.files['profile']

        filename = secure_filename(profile.filename)
        profile_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile.save(profile_path)

        user = User(username=username, email=email, password=password, profile_pic=filename)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/call')
@login_required
def call():
    return render_template('call.html')

# SocketIO handlers
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
