import datetime
import dateutil.tz


from flask import Blueprint, render_template, request, redirect, url_for, abort
import flask_login


from . import model, db


bp = Blueprint("main", __name__)


@bp.route("/")
@flask_login.login_required
def index():
    user = model.User(email="mary@example.com", name="hubert")
    query = db.select(model.Post).where(model.Post.response_to_id==None).order_by(model.Post.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    followers = db.aliased(model.User)
    following_query = (
        db.select(model.Post)
        .join(model.User)
        .join(followers, model.User.followers)
        .where(followers.id == flask_login.current_user.id)
        .where(model.Post.response_to == None)
        .order_by(model.Post.timestamp.desc())
        .limit(10)
    )
    return render_template("main/index.html", posts=posts)

@bp.route("/profile/<int:user_id>")
@flask_login.login_required
def profile(user_id):
    user = db.get_or_404(model.User, user_id)
    query = db.select(model.Post).filter_by(user=user).where(model.Post.response_to_id==None).order_by(model.Post.timestamp.desc())
    posts = db.session.execute(query).scalars().all()

    if (flask_login.current_user == user_id):
        follow_button = None
    elif (flask_login.current_user in user.followers):
        follow_button = "unfollow"
    else:
        follow_button = "follow"

    return render_template("main/user_template.html", user=user, posts=posts, follow_button=follow_button)

@bp.route("/post", methods=["POST"])
@flask_login.login_required
def new_post():
    user = flask_login.current_user
    text = request.form.get("text")
    response_to = request.form.get("response_to")

    if response_to:
        response_to_post = db.get_or_404(model.Post, response_to)

    new_post = model.Post(user=user, text=text, response_to_id=response_to, timestamp=datetime.datetime.now(dateutil.tz.tzlocal()))
    
    db.session.add(new_post)
    db.session.commit()
    
    if response_to:
        return redirect(url_for("main.post", post_id=response_to))
    else:
        return redirect(url_for("main.post", post_id=new_post.id))

@bp.route("/post/<int:post_id>")
@flask_login.login_required
def post(post_id):
    post = db.get_or_404(model.Post, post_id)
    if (post.response_to_id is not None):
        abort(403)
    query = db.select(model.Post).filter_by(response_to_id=post_id).order_by(model.Post.timestamp.desc())
    responses = db.session.execute(query).scalars().all()
    return render_template("main/post.html", post=post, responses=responses)

@bp.route("/follow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def follow(user_id):
    user = db.get_or_404(model.User, user_id)
    if (flask_login.current_user not in user.followers):
        user.followers.append(flask_login.current_user)
        db.session.commit()
    return redirect(url_for("main.profile", user_id=user_id))


@bp.route("/unfollow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def unfollow(user_id):
    user = db.get_or_404(model.User, user_id)
    if (flask_login.current_user in user.followers):
        user.followers.remove(flask_login.current_user)
        db.session.commit()
    return redirect(url_for("main.profile", user_id=user_id))