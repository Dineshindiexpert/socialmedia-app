from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Post, Story, Message
from app import db, login_manager
import os
from werkzeug.utils import secure_filename
from datetime import datetime

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        avatar = request.files['avatar']
        avatar_filename = secure_filename(avatar.filename)
        avatar.save(os.path.join('app/static/avatars', avatar_filename))

        user = User(username=username, email=email, password=password, avatar=avatar_filename)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/home')
@login_required
def home():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    stories = Story.query.order_by(Story.timestamp.desc()).all()
    users = User.query.all()
    return render_template('home.html', posts=posts, stories=stories, users=users)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/upload_post', methods=['POST'])
@login_required
def upload_post():
    image = request.files['image']
    caption = request.form['caption']
    filename = secure_filename(image.filename)
    image.save(os.path.join('app/static/uploads', filename))

    post = Post(image=filename, caption=caption, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('main.home'))

@main.route('/upload_story', methods=['POST'])
@login_required
def upload_story():
    image = request.files['story']
    filename = secure_filename(image.filename)
    image.save(os.path.join('app/static/stories', filename))

    story = Story(image=filename, user_id=current_user.id)
    db.session.add(story)
    db.session.commit()
    return redirect(url_for('main.home'))

@main.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, posts=posts)

@main.route('/chat')
@login_required
def chat():
    users = User.query.all()
    return render_template('chat.html', users=users)
@main.route('/story/<int:story_id>')
@login_required
def story_view(story_id):
    story = Story.query.get_or_404(story_id)
    user = User.query.get(story.user_id)
    return render_template('story_view.html', story=story, story_user=user)
@main.route('/like/<int:post_id>')
@login_required
def like(post_id):
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post_id))
    db.session.commit()
    return redirect(url_for('main.home'))

@main.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    text = request.form['text']
    db.session.add(Comment(user_id=current_user.id, post_id=post_id, text=text))
    db.session.commit()
    return redirect(url_for('main.home'))
@main.route('/story/<int:story_id>')
@login_required
def story_view(story_id):
    story = Story.query.get_or_404(story_id)
    user = User.query.get(story.user_id)

    # Get all story IDs ordered by ID
    all_stories = Story.query.order_by(Story.id).all()
    story_ids = [s.id for s in all_stories]
    current_index = story_ids.index(story_id)

    prev_story_id = story_ids[current_index - 1] if current_index > 0 else None
    next_story_id = story_ids[current_index + 1] if current_index < len(story_ids) - 1 else None

    return render_template(
        'story_view.html',
        story=story,
        story_user=user,
        prev_story_id=prev_story_id,
        next_story_id=next_story_id
    )
