from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.utils import secure_filename
import os
from .forms import RegisterForm, LoginForm
from .models import users_db, User, friend_requests, friendships

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        pic = form.profile_pic.data

        filename = secure_filename(pic.filename)
        path = os.path.join('app/static/uploads', filename)
        pic.save(path)

        users_db[email] = User(username, email, password, filename)
        flash("Registered successfully.")
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = users_db.get(email)
        if user and user.check_password(password):
            session['user_email'] = email
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html', form=form)

@main.route('/dashboard')
def dashboard():
    email = session.get('user_email')
    if not email or email not in users_db:
        return redirect(url_for('main.login'))
    user = users_db[email]
    return render_template('dashboard.html', user=user, users_db=users_db, friend_requests=friend_requests, friendships=friendships)

@main.route('/chat')
def chat():
    email = session.get('user_email')
    if not email or email not in users_db:
        return redirect(url_for('main.login'))
    user = users_db[email]
    return render_template('chat.html', username=user.username)

@main.route('/call')
def call():
    email = session.get('user_email')
    if not email or email not in users_db:
        return redirect(url_for('main.login'))
    user = users_db[email]
    return render_template('call.html', username=user.username)

@main.route('/send_request', methods=['POST'])
def send_request():
    sender = session.get('user_email')
    receiver = request.form.get('receiver_email')

    if not receiver or receiver not in users_db:
        flash("User not found.")
        return redirect(url_for('main.dashboard'))

    if receiver not in friend_requests:
        friend_requests[receiver] = []
    if sender not in friend_requests[receiver]:
        friend_requests[receiver].append(sender)

    flash("Friend request sent.")
    return redirect(url_for('main.dashboard'))

@main.route('/accept_request/<sender_email>')
def accept_request(sender_email):
    receiver = session.get('user_email')
    if receiver in friend_requests and sender_email in friend_requests[receiver]:
        friend_requests[receiver].remove(sender_email)
        friendships.setdefault(receiver, []).append(sender_email)
        friendships.setdefault(sender_email, []).append(receiver)
        flash("Friend added.")
    return redirect(url_for('main.dashboard'))

@main.route('/reject_request/<sender_email>')
def reject_request(sender_email):
    receiver = session.get('user_email')
    if receiver in friend_requests and sender_email in friend_requests[receiver]:
        friend_requests[receiver].remove(sender_email)
        flash("Request rejected.")
    return redirect(url_for('main.dashboard'))
from .models import posts

@main.route('/upload_post', methods=['GET', 'POST'])
def upload_post():
    email = session.get('user_email')
    if not email or email not in users_db:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        caption = request.form.get('caption')
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        save_path = os.path.join('app/static/uploads/posts', filename)
        photo.save(save_path)

        posts.append({
            'email': email,
            'image': filename,
            'caption': caption,
            'likes': 0,
            'comments': []
        })
        flash("Post uploaded successfully.")
        return redirect(url_for('main.view_posts'))

    return render_template('upload_post.html')

@main.route('/posts')
def view_posts():
    return render_template('posts.html', posts=posts, users_db=users_db)

@main.route('/like_post/<int:post_id>')
def like_post(post_id):
    if 0 <= post_id < len(posts):
        posts[post_id]['likes'] += 1
    return redirect(url_for('main.view_posts'))

@main.route('/comment_post/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    comment = request.form.get('comment')
    email = session.get('user_email')
    if 0 <= post_id < len(posts) and comment:
        posts[post_id]['comments'].append({
            'email': email,
            'text': comment
        })
    return redirect(url_for('main.view_posts'))
