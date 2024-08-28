from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment
from . import db

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        
        title=request.form.get('title')
        text = request.form.get('text')
        

        if not title:
            flash('Title is required.',category='error')
        elif not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(title=title,text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('create_post.html', user=current_user)



@views.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def open_post(id):
    post = Post.query.get_or_404(id)
    show_collapse = request.args.get('show_collapse', 'false') == 'true'
    print('request_args', request.args.get('show_collapse'))
    print('show_collapse', show_collapse)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.text = request.form.get('text')

        if not post.title:
            flash('Title is required!', category='error')
        elif not post.description:
            flash('Description is required!', category='error')
        else:
            db.session.commit()
            return redirect(url_for('views.home'))

    return render_template('view_post.html', post=post, user=current_user, show_collapse=show_collapse)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')
        

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User does not exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("user_allposts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.open_post',id=post_id,show_collapse='true'))


@views.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    post_id = comment.post_id


    if not comment:
        flash('Comment does not exist.', category='error')
        return redirect(url_for(views.home))
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('Permission Denied!', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment Deleted',category='success')
    return redirect(url_for('views.open_post', id=post_id, show_collapse='true'))




@views.route("/update-post/<id>", methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
        return redirect(url_for('views.home'))
    if current_user.id != post.author:
        flash('Permission Denied.', category='error')
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        title=request.form.get('title')
        text = request.form.get('text')
        if not text:
            flash('Post content cannot be empty!', category='error')
        else:
            post.text = text
            post.title= title
            db.session.commit()
            flash('Post updated successfully!', category='success')
            return redirect(url_for('views.open_post', id=post.id))
    return render_template('update_post.html', post=post, user=current_user)






