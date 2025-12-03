import datetime
import dateutil.tz


from flask import Blueprint, flash, render_template, request, redirect, url_for, abort
import flask_login

from . import model, db


bp = Blueprint("main", __name__)

upload_folder = "static/resources"


@bp.route("/")
@flask_login.login_required
def index():
    query = db.select(model.TripProposal).where(model.TripProposal.status == model.TripProposalStatus.OPEN).order_by(model.TripProposal.timestamp.desc()).limit(9)
    # messages = db.session.execute(query).scalars().all()
    # trip_proposals = db.aliased(model.User)
    # following_query = (
    #     db.select(model.TripProposal)
    #     .join(model.User)
    #     .join(trip_proposals, model.User.trip_proposals)
    #     .where(trip_proposals.id == flask_login.current_user.id)
    #     .order_by(model.TripProposal.timestamp.desc())
    #     .limit(10)
    # )
    latest_trips = db.session.execute(query).scalars().all()
    
    return render_template("main/index.html", latest_trips=latest_trips)

@bp.route("/profile/<int:user_id>")
@flask_login.login_required
def profile(user_id):
    user = db.get_or_404(model.User, user_id)

    # Load all trips the user participates in
    query = (
        db.select(model.TripProposal)
        .join(model.TripProposal.participants)
        .filter(model.User.id == user.id)
        .order_by(model.TripProposal.timestamp.desc())
    )
    trips = db.session.execute(query).scalars().all()

    # Follow button logic
    if flask_login.current_user.id == user.id:
        follow_button = None
    elif hasattr(user, "followers") and flask_login.current_user in user.followers:
        follow_button = "unfollow"
    else:
        follow_button = "follow"

    return render_template(
        "main/user_template.html",
        user=user,
        trips=trips,
        follow_button=follow_button,
    )

@bp.route("/trip", methods=["POST"])
@flask_login.login_required
def new_trip():
    user = flask_login.current_user
    title = request.form.get("title")
    description = request.form.get("description")
    origin = request.form.get("departure_location")
    destinations = request.form.getlist("destination")
    start = request.form.get("start")
    end = request.form.get("end")
    budget = request.form.get("budget")
    max_members = request.form.get("max_members")
    minAge = request.form.get("minAge")
    maxAge = request.form.get("maxAge")
    status=model.TripProposalStatus.OPEN.value

    #since our model stores 'destinations' as a comma separated string
    destinations_str = ",".join(destinations) 


    #response_to = request.form.get("response_to")

   # if response_to:
       # response_to_trip = db.get_or_404(model.TripProposal, response_to)

    new_trip = model.TripProposal(
        creator=user,
        participants={user}, 
        title=title, 
        description=description,
        response_to_id=0, 
        origin=origin, 
        destinations=destinations_str, 
        start_date=start, 
        end_date=end, 
        budget= budget, 
        max_travelers=max_members,
        min_age=minAge,
        max_age=maxAge,
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
        status=status
        )
    
    db.session.add(new_trip)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=new_trip.id))

    
   # if response_to:
        #return redirect(url_for("main.trip", trip_id=response_to))
   # else:
       # return redirect(url_for("main.trip", trip_id=new_trip.id))

       

@bp.route("/trip/<int:trip_id>")
@bp.route("/trip/<int:trip_id>/forum/<forum_topic>")
@flask_login.login_required
def trip(trip_id, forum_topic=None):
    trip = db.get_or_404(model.TripProposal, trip_id)
    #if (trip.response_to_id is not None):
    #    abort(403)
    query = db.select(model.TripProposal).filter_by(response_to_id=trip_id).order_by(model.TripProposal.timestamp.desc())
    responses = db.session.execute(query).scalars().all()
    user = flask_login.current_user
    already_joined = user in trip.participants

    topics_query = (db.select(model.TripProposalMessage.forum_topic).where(model.TripProposal.id == trip_id).distinct().order_by(model.TripProposalMessage.forum_topic))
    forum_topics = db.session.execute(topics_query).scalars().all()
    if forum_topic:
        active_topic = forum_topic
    else:
        active_topic = "Main"

    active_forum_messages_query = (db.select(model.TripProposalMessage).where(model.TripProposal.id == trip_id, model.TripProposalMessage.forum_topic == active_topic).order_by(model.TripProposalMessage.timestamp.asc()))
    active_forum_messages = db.session.execute(active_forum_messages_query).scalars().all()

    return render_template("main/trip.html", trip=trip, responses=responses, already_joined = already_joined, forum_topics = forum_topics, active_topic = active_topic, active_forum_messages = active_forum_messages)



@bp.route("/trip/<int:trip_id>/join", methods=["POST"])
@flask_login.login_required
def join_trip(trip_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user

    if user in trip.participants:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    if trip.max_travelers is not None and len(trip.participants) >= trip.max_travelers:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    if trip.max_age is not None and trip.min_age is not None:
        if trip.min_age > user.age or trip.max_age < user.age:
            return redirect(url_for("main.trip", trip_id=trip_id))
        
    joining_user = model.TripProposalParticipation(
        user_id=user.id,
        trip_proposal_id=trip.id,
        is_editor=False,
    )
    db.session.add(joining_user)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/trip/<int:trip_id>/message", methods=["POST"])
@flask_login.login_required
def new_message(trip_id):
    user = flask_login.current_user
    content = request.form.get("message-content", "").strip()
    forum_topic = request.form.get("forum_topic", "Main").strip() #to get the specific channel/forum of the messages
    new_forum_topic = request.form.get("new_forum_topic", "").strip() #if user wants to make a new forum for some specific messages
    if new_forum_topic:
        forum_topic = new_forum_topic

    if not content:
        flash("Message cannot be empty", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    message = model.TripProposalMessage(trip_proposal_id=trip_id, user_id = flask_login.current_user.id, content=content, forum_topic = forum_topic)
    db.session.add(message)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id, forum_topic = forum_topic))

@bp.route("/form")
@flask_login.login_required
def form():
    return render_template("main/trip_form.html")

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