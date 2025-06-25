from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from .models import db, User, Post, Comment, Like, Story
import os
import uuid

main = Blueprint('main', __name__)

# Home route
@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

# Dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    stories = Story.query.order_by(Story.timestamp.desc()).all()
    return render_template('dashboard.html', posts=posts, stories=stories)

# Upload post
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_post():
    if request.method == 'POST':
        file = request.files['file']
        caption = request.form.get('caption')

        if file:
            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            filepath = os.path.join('app/static/uploads', unique_filename)
            file.save(filepath)

            post = Post(user_id=current_user.id, image_file=unique_filename, caption=caption)
            db.session.add(post)
            db.session.commit()

            flash("Post uploaded successfully!", "success")
            return redirect(url_for('main.dashboard'))

    return render_template('upload_post.html')

# Like post
@main.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
    db.session.commit()
    return jsonify({'likes': len(post.likes)})

# Comment post
@main.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form.get('comment')
    if content:
        comment = Comment(user_id=current_user.id, post_id=post_id, content=content)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('main.dashboard'))

# Profile
@main.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

# Story view (✅ keep only this one!)
@main.route('/story/<int:story_id>')
@login_required
def story_view(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('story_view.html', story=story)
