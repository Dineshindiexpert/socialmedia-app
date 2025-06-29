import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db, login_manager, socketio
from app.models import User, FriendRequest
from flask_socketio import emit
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

main = Blueprint('main', __name__)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('dashboard')) if current_user.is_authenticated else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        profile = request.files['profile']

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
        else:
            filename = secure_filename(profile.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile.save(filepath)
            new_user = User(username=username, email=email, password=password, profile_pic=filename)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    all_users = User.query.filter(User.id != current_user.id).all()
    friend_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    return render_template('dashboard.html', user=current_user, users=all_users, requests=friend_requests)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/send_request/<int:user_id>')
@login_required
def send_request(user_id):
    if not FriendRequest.query.filter_by(sender_id=current_user.id, receiver_id=user_id).first():
        fr = FriendRequest(sender_id=current_user.id, receiver_id=user_id)
        db.session.add(fr)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/accept_request/<int:request_id>')
@login_required
def accept_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if fr and fr.receiver_id == current_user.id:
        fr.status = 'accepted'
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/decline_request/<int:request_id>')
@login_required
def decline_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if fr and fr.receiver_id == current_user.id:
        fr.status = 'declined'
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/chat')
@login_required
def chat():
    friends = db.session.query(User).join(FriendRequest, ((FriendRequest.sender_id==User.id) | (FriendRequest.receiver_id==User.id)))\
        .filter(FriendRequest.status=='accepted', ((FriendRequest.sender_id==current_user.id) | (FriendRequest.receiver_id==current_user.id)), User.id != current_user.id).distinct()
    return render_template('chat.html', user=current_user, friends=friends)

@app.route('/call')
@login_required
def call():
    return render_template('calls.html')

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
@socketio.on("send_message")
def handle_send_message(data):
    emit("receive_message", {
        "username": current_user.username,
        "message": data["message"]
    }, broadcast=True)
