import os
from flask import render_template, url_for, flash, redirect, request, abort, session
from app import app, db, socketio
from app.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_socketio import emit, join_room, leave_room

# Helper: allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

# ---------- Authentication Routes ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        # Basic validations:
        if not username or not email or not password:
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('register'))
        # Check existing
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))
        # Handle profile picture
        file = request.files.get('profile_pic')
        if file and file.filename != '':
            if allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename = secure_filename(file.filename)
                unique_name = f"{username}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(filepath)
                profile_pic_name = unique_name
            else:
                flash('Invalid image format for profile picture.', 'warning')
                profile_pic_name = 'default.jpg'
        else:
            profile_pic_name = 'default.jpg'
        # Hash password
        hashed_pw = generate_password_hash(password)
        # Create user
        user = User(username=username, email=email, password=hashed_pw, profile_pic=profile_pic_name)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Check email and password', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Home route
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# ---------- Dashboard & Posts ----------

@app.route('/dashboard')
@login_required
def dashboard():
    # Show feed: all posts or from followed users (for simplicity: all)
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('dashboard.html', posts=posts)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        caption = request.form.get('caption', '').strip()
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('upload'))
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        if allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
            media_type = 'image'
        elif allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS):
            media_type = 'video'
        else:
            flash('Unsupported file type.', 'warning')
            return redirect(url_for('upload'))
        # Create unique filename
        unique_name = f"{current_user.username}_{int(datetime.utcnow().timestamp())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        # Save Post
        post = Post(caption=caption, filename=unique_name, media_type=media_type, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post uploaded!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('upload_post.html')

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    # For simplicity: increment likes (no unlike or tracking per user)
    post.likes = post.likes + 1
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    text = request.form.get('comment', '').strip()
    if text:
        comm = Comment(text=text, user_id=current_user.id, post_id=post.id)
        db.session.add(comm)
        db.session.commit()
    return redirect(url_for('dashboard'))

# ---------- Profile ----------

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username').strip()
    bio = request.form.get('bio', '').strip()
    file = request.files.get('profile_pic')
    # Validate username uniqueness if changed
    if username and username != current_user.username:
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'warning')
            return redirect(url_for('profile'))
        current_user.username = username
    current_user.bio = bio
    if file and file.filename != '':
        if allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = secure_filename(file.filename)
            unique_name = f"{current_user.username}_{int(datetime.utcnow().timestamp())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            current_user.profile_pic = unique_name
        else:
            flash('Invalid image format.', 'warning')
    db.session.commit()
    flash('Profile updated.', 'success')
    return redirect(url_for('profile'))


# ---------- Chat (SocketIO) ----------

# A simple broadcast chat room. For private chat or rooms, you’d handle rooms/IDs.
@socketio.on('send_message')
def handle_send_message(msg):
    user = current_user.username if current_user.is_authenticated else 'Anonymous'
    full_msg = f"{user}: {msg}"
    # Broadcast to all
    emit('receive_message', full_msg, broadcast=True)

# ---------- Call signaling (SocketIO) ----------

@socketio.on('video-offer')
def handle_video_offer(offer):
    # Broadcast offer to other clients
    emit('video-offer', offer, broadcast=True, include_self=False)

@socketio.on('video-answer')
def handle_video_answer(answer):
    emit('video-answer', answer, broadcast=True, include_self=False)

@socketio.on('ice-candidate')
def handle_ice_candidate(candidate):
    emit('ice-candidate', candidate, broadcast=True, include_self=False)

@socketio.on('end-call')
def handle_end_call():
    emit('end-call', broadcast=True, include_self=False)
