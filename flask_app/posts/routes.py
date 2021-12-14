import io
import base64

from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from ..models import User, Post, Comment
from ..forms import LikeForm, UnlikeForm, CreatePostForm, FollowForm, UnfollowForm, CommentForm
from ..utils import current_time

posts = Blueprint("posts", __name__)


def get_b64_img(post):
    bytes_im = io.BytesIO(post.image.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


@posts.route("/", methods=["GET", "POST"])
@login_required
def index():

    # get posts of users that current_user follows
    follows = current_user.following

    # # adds user to follows list
    # follows = current_user.following
    # follows.append('newUsername')
    # current_user.update(following=follows)

    # get posts of followed users
    posts = []
    for user_id in follows:
        user = User.objects(uid=user_id).first()
        for post in Post.objects(poster=user):
            posts.append(post)

    posts = [{
        'poster_name': post.poster.username,
        'poster_id': post.poster.uid,
        'image': get_b64_img(post),
        'caption': post.caption,
        'date': post.date,
        'num_likes': len(post.likers),
        'post_id': post.id,
    } for post in posts]

    return render_template("index.html", posts=posts)

# display num followers, following
# display "follow" button
# display posts, similar to posts.index


@posts.route("/post/<id>", methods=["GET", "POST"])
@login_required
def post_detail(id):
    # get post
    post = Post.objects(id=id).first()

    if post is None:
        return render_template('404.html')

    post_dict = {
        'poster_name': post.poster.username,
        'poster_id': post.poster.uid,
        'image': get_b64_img(post),
        'caption': post.caption,
        'date': post.date,
        'num_likes': len(post.likers),
        'post_id': post.id,
    }

    if current_user._get_current_object() not in post.likers:
        form = LikeForm(prefix='1')
        if form.validate_on_submit():
            new_likers = post.likers
            new_likers.append(current_user._get_current_object())
            post.likers = new_likers
            post.save()
            return redirect(request.path)
    else:
        form = UnlikeForm(prefix='1')
        if form.validate_on_submit():
            new_likers = post.likers
            new_likers.remove(current_user._get_current_object())
            post.likers = new_likers
            post.save()
            return redirect(request.path)

    comments = Comment.objects(post=post)

    comment_form = CommentForm(prefix='2')

    if comment_form.validate_on_submit():
        comment = Comment(
            post=post,
            commenter=current_user._get_current_object(),
            content=comment_form.text.data,
            date=current_time(),
        )
        comment.save()
        return redirect(request.path)

    # get likers
    return render_template("post_detail.html", post=post_dict, like_form=form,
                           comment_form=comment_form, comments=comments)

# display num followers, following
# display "follow" button
# display posts, similar to posts.index


@posts.route("/user/<uid>", methods=["GET", "POST"])
@login_required
def user_detail(uid):
    user = User.objects(uid=uid).first()

    if user is None:
        return render_template('404.html')

    # get followers
    followers = []
    for u in User.objects():
        if uid in u.following:
            followers.append(u)

    # if true, current user follows this person
    # current user follows and unfollows at user detail page
    if current_user._get_current_object() in followers:
        form = UnfollowForm()
        if form.validate_on_submit():
            new_following = current_user.following
            new_following.remove(uid)
            current_user.following = new_following
            current_user.save()
            return redirect(request.path)
    else:
        form = FollowForm()
        if form.validate_on_submit():
            new_following = current_user.following
            new_following.append(uid)
            current_user.following = new_following
            current_user.save()
            return redirect(request.path)

    following = user.following

    # get users posts
    posts = Post.objects(poster=user)
    posts = [{
        'poster_name': user.username,
        'poster_id': user.uid,
        'image': get_b64_img(post),
        'caption': post.caption,
        'date': post.date,
        'num_likes': len(post.likers),
        'post_id': post.id,
    } for post in posts]

    return render_template("user_detail.html", username=user.username,
                           posts=posts, follow_form=form, num_followers=len(
                               followers),
                           num_following=len(following))


@posts.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    post_form = CreatePostForm()

    if post_form.validate_on_submit():
        # image stuff
        img = post_form.picture.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'

        post = Post(
            poster=current_user._get_current_object(),
            caption=post_form.caption.data,
            date=current_time(),
            likers=[],
        )
        post.image.put(img.stream, content_type=content_type)
        post.save()
        return redirect(request.path)

    return render_template("create_post.html", form=post_form)
