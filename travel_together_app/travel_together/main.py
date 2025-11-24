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
    query = db.select(model.TripProposal).where(model.TripProposal.status == model.TripProposalStatus.OPEN).order_by(model.TripProposal.timestamp.desc()).limit(10)
    messages = db.session.execute(query).scalars().all()
    trip_proposals = db.aliased(model.User)
    following_query = (
        db.select(model.TripProposal)
        .join(model.User)
        .join(trip_proposals, model.User.trip_proposals)
        .where(trip_proposals.id == flask_login.current_user.id)
        .order_by(model.TripProposal.timestamp.desc())
        .limit(10)
    )
    return render_template("main/index.html", messages=messages)

@bp.route("/profile/<int:user_id>")
@flask_login.login_required
def profile(user_id):
    user = db.get_or_404(model.User, user_id)
    query = db.select(model.TripProposal).filter_by(user=user).where(model.TripProposal.response_to_id==None).order_by(model.TripProposal.timestamp.desc())
    messages = db.session.execute(query).scalars().all()

    if (flask_login.current_user == user_id):
        follow_button = None
    elif (flask_login.current_user in user.trip_proposals):
        follow_button = "unfollow"
    else:
        follow_button = "follow"

    return render_template("main/user_template.html", user=user, messages=messages, follow_button=follow_button)

@bp.route("/trip", methods=["POST"])
@flask_login.login_required
def new_trip():
    user = flask_login.current_user
    text = request.form.get("text")
    response_to = request.form.get("response_to")

    if response_to:
        response_to_trip = db.get_or_404(model.TripProposal, response_to)

    new_trip = model.TripProposal(participants=(user), text=text, response_to_id=response_to, timestamp=datetime.datetime.now(dateutil.tz.tzlocal()))
    
    db.session.add(new_trip)
    db.session.commit()
    
    if response_to:
        return redirect(url_for("main.trip", trip_id=response_to))
    else:
        return redirect(url_for("main.trip", trip_id=new_trip.id))

@bp.route("/trip/<int:trip_id>")
@flask_login.login_required
def trip(trip_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    if (trip.response_to_id is not None):
        abort(403)
    query = db.select(model.TripProposal).filter_by(response_to_id=trip_id).order_by(model.TripProposal.timestamp.desc())
    responses = db.session.execute(query).scalars().all()
    return render_template("main/trip.html", trip=trip, responses=responses)

@bp.route("/follow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def follow(user_id):
    user = db.get_or_404(model.User, user_id)
    if (flask_login.current_user not in user.trip_proposals):
        user.trip_proposals.append(flask_login.current_user)
        db.session.commit()
    return redirect(url_for("main.profile", user_id=user_id))


@bp.route("/unfollow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def unfollow(user_id):
    user = db.get_or_404(model.User, user_id)
    if (flask_login.current_user in user.trip_proposals):
        user.trip_proposals.remove(flask_login.current_user)
        db.session.commit()
    return redirect(url_for("main.profile", user_id=user_id))