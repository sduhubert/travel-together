from datetime import datetime
import os
import dateutil.tz


from flask import Blueprint, current_app, flash, jsonify, render_template, request, redirect, url_for, abort
import flask_login

from werkzeug.utils import secure_filename

from . import model, db
from sqlalchemy import or_

bp = Blueprint("main", __name__)

upload_folder = "static/resources"


@bp.route("/")
@flask_login.login_required
def index():
    query = db.select(model.TripProposal).where(or_(
        model.TripProposal.status == model.TripProposalStatus.OPEN.value,
        model.TripProposal.status == model.TripProposalStatus.APPROVAL_REQUIRED.value)
    ).order_by(model.TripProposal.timestamp.desc()).limit(4)
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
    minAge = request.form.get("min")
    maxAge = request.form.get("max")
    university = request.form.get("university_specific")
    status =model.TripProposalStatus.OPEN.value
    image = request.files.get("trip_image")
    if image and image.filename != "":
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.static_folder, "resources", filename)
        image.save(save_path)
    else:
        filename = "example-trip-1.jpg"

    #since our model stores 'destinations' as a comma separated string
    destinations_str = ",".join(destinations) 

    new_trip = model.TripProposal(
        creator=user,
        title=title, 
        description=description,
        origin=origin, 
        destinations=destinations_str, 
        start_date=start, 
        end_date=end, 
        budget= budget, 
        max_travelers=max_members,
        min_age=minAge,
        max_age=maxAge,
        university = university,
        timestamp=datetime.now(dateutil.tz.tzlocal()),
        status=status,
        image=filename
        )
    
    db.session.add(new_trip)
    db.session.commit()
    
    participation = model.TripProposalParticipation(
        user_id=user.id,
        trip_proposal_id=new_trip.id,
        is_editor=True
    )

    db.session.add(participation)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=new_trip.id))

@bp.route("/make_editor/<int:trip_id>/<int:participant_id>", methods=["POST"])
@flask_login.login_required
def make_editor(trip_id, participant_id):
    trip = model.TripProposal.query.get_or_404(trip_id)
    user = flask_login.current_user
    
    if not user.is_editor_for(trip):
        flash("You do not have permission to promote editors for this trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    editor = model.TripProposalParticipation.query.get((participant_id, trip.id))
    editor.is_editor = True
    db.session.commit()
    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/edit_trip/<int:trip_id>", methods=["POST"])
@flask_login.login_required
def edit_trip(trip_id):
    trip = model.TripProposal.query.get_or_404(trip_id)
    user = flask_login.current_user
    
    participation = model.TripProposalParticipation.query.get((user.id, trip.id))
    
    if trip.status == model.TripProposalStatus.FINALIZED or trip.status == model.TripProposalStatus.CANCELLED:
        flash("This trip has been finalized or cancelled and cannot be edited.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))

    if (user not in trip.participants) and not (participation and participation.is_editor):
        flash("You do not have permission to edit this trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    
    status = request.form.get("status")
    if trip.status in [2, 3, 4]:
        flash("This trip is closed and cannot be modified.", "error")
        return redirect(url_for('main.trip', trip_id=trip.id))
    
    origin = request.form.get("departure_location", "").strip()
    
    destinations = [d.strip() for d in request.form.getlist("destination") if d.strip()]
    destinations_str = ",".join(destinations) 
    
    start = request.form.get("start")
    end = request.form.get("end")
    
    budget = request.form.get("budget")
    max_members = request.form.get("max_members")
    minAge = request.form.get("min_age")
    maxAge = request.form.get("max_age")
    university = request.form.get("university_specific") or None

    if university == "":
        university = None
    
    image = request.files.get("trip_image")
    
    if trip.title != title:
        trip.title = title

    if trip.description != description:
        trip.description = description
        
    if status and trip.status != status:
        trip.status = status
        
    trip.origin_finalized = 'origin_finalized' in request.form
    trip.destinations_finalized = 'destinations_finalized' in request.form
    trip.dates_finalized = 'dates_finalized' in request.form
    trip.budget_finalized = 'budget_finalized' in request.form
    trip.max_travelers_finalized = 'max_travelers_finalized' in request.form
    trip.age_range_finalized = 'age_range_finalized' in request.form
    trip.status_finalized = 'status_finalized' in request.form
    trip.university_finalized ='university_finalized' in request.form
    if not trip.origin_finalized and origin and trip.origin != origin:
        trip.origin = origin

    if not trip.destinations_finalized and destinations_str and trip.destinations != destinations_str:
        trip.destinations = destinations_str

    if not trip.dates_finalized:
        if start and trip.start_date != start:
            trip.start_date = start
        if end and trip.end_date != end:
            trip.end_date = end
    if not trip.budget_finalized and budget and trip.budget != budget:
        trip.budget = budget
    if not trip.max_travelers_finalized and max_members and trip.max_travelers != max_members:
        trip.max_travelers = max_members
    if not trip.age_range_finalized:
        if minAge and trip.min_age != minAge:
            trip.min_age = minAge
        if maxAge and trip.max_age != maxAge:
            trip.max_age = maxAge
    if not trip.university_finalized:
        if trip.university != university:
            trip.university = university
    if image and image.filename and image.filename != trip.image:
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.static_folder, "resources", filename)
        image.save(save_path)
        trip.image = filename
    
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))
       

@bp.route("/trip/<int:trip_id>")
@bp.route("/trip/<int:trip_id>/forum/<forum_topic>")
@flask_login.login_required
def trip(trip_id, forum_topic=None):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user
    already_joined = user in trip.participants
    
    trip_admin = False
    join_requests = []
    requesting_users = []
    
    if already_joined:
        is_editor_query = db.select(model.TripProposalParticipation.is_editor).where(
            model.TripProposalParticipation.user_id == user.id,
            model.TripProposalParticipation.trip_proposal_id == trip.id
        )
        is_editor = db.session.execute(is_editor_query).scalar_one_or_none()
        if is_editor:
            trip_admin = True
            if trip.status == model.TripProposalStatus.APPROVAL_REQUIRED.value:
                join_requests_query = db.select(model.TripProposalJoinRequest).where(model.TripProposalJoinRequest.trip_proposal_id == trip.id).order_by(model.TripProposalJoinRequest.timestamp.asc())
                join_requests = db.session.execute(join_requests_query).scalars().all()
                for req in join_requests:
                    requesting_users.append(db.get_or_404(model.User, req.user_id))
                join_requests = [(req, user) for req, user in zip(join_requests, requesting_users)]

    topics_query = (db.select(model.TripProposalMessage.forum_topic).where(model.TripProposalMessage.trip_proposal_id == trip_id).distinct().order_by(model.TripProposalMessage.forum_topic))
    forum_topics = db.session.execute(topics_query).scalars().all()
    if forum_topic:
        active_topic = forum_topic
    else:
        active_topic = "Main"

    active_forum_messages_query = (db.select(model.TripProposalMessage).where(model.TripProposalMessage.trip_proposal_id == trip_id, model.TripProposalMessage.forum_topic == active_topic).order_by(model.TripProposalMessage.timestamp.asc()))
    active_forum_messages = db.session.execute(active_forum_messages_query).scalars().all()

    return render_template("main/trip.html", trip=trip, statuses=model.TripProposalStatus, join_requests=join_requests, already_joined = already_joined, forum_topics = forum_topics, active_topic = active_topic, active_forum_messages = active_forum_messages)

@bp.route("/trip/<int:trip_id>/join", methods=["POST"])
@flask_login.login_required
def join_trip(trip_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user

    if trip.status != model.TripProposalStatus.OPEN.value:
        flash("This trip is not open for joining.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))

    if user in trip.participants:
        flash("You are already part of this trip!", "info")
        return redirect(url_for("main.trip", trip_id=trip_id))

    if trip.max_travelers is not None and len(trip.participants) >= trip.max_travelers:
        flash("Trip is already full!", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))

    if trip.age_range_finalized:
        if trip.min_age and user.age < trip.min_age:
            flash("You are too young for this trip.", "error")
            return redirect(url_for("main.trip", trip_id=trip_id))
        if trip.max_age and user.age > trip.max_age:
            flash("You are too old for this trip.", "error")
            return redirect(url_for("main.trip", trip_id=trip_id))

    if trip.university_finalized and trip.university:
        if not user.university or user.university != trip.university:
            flash("This trip is restricted to a specific university.", "error")
            return redirect(url_for("main.trip", trip_id=trip_id))

    participation = model.TripProposalParticipation(
        user_id=user.id,
        trip_proposal_id=trip.id,
        is_editor=False,
    )
    db.session.add(participation)
    db.session.commit()

    flash("Successfully joined the trip!", "success")
    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/trip/<int:trip_id>/request_join", methods=["POST"])
@flask_login.login_required
def request_join_trip(trip_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user

    if user in trip.participants:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    existing_request = db.session.get(model.TripProposalJoinRequest, (trip.id, user.id))
    if existing_request:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    join_request = model.TripProposalJoinRequest(
        trip_proposal_id=trip.id,
        user_id=user.id,
    )
    db.session.add(join_request)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/trip/<int:trip_id>/update_join_request/<int:requesting_user_id>", methods=["POST"])
@flask_login.login_required
def update_join_request(trip_id, requesting_user_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user

    if not user.is_editor_for(trip):
        flash("You do not have permission to manage join requests for this trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    action = request.form.get("approval_status")
    join_request = db.session.get(model.TripProposalJoinRequest, (trip.id, requesting_user_id))
    if not join_request:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    if action == "approve":
        joining_user = model.TripProposalParticipation(
            user_id=requesting_user_id,
            trip_proposal_id=trip.id,
            is_editor=False,
        )
        db.session.add(joining_user)
    
    db.session.delete(join_request)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/trip/<int:trip_id>/cancel_join", methods=["POST"])
@flask_login.login_required
def cancel_join_request(trip_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user

    existing_request = db.session.get(model.TripProposalJoinRequest, (trip.id, user.id))
    if not existing_request:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    db.session.delete(existing_request)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/trip/<int:trip_id>/leave", methods=["POST"])
@flask_login.login_required
def leave_trip(trip_id):
    trip = db.get_or_404(model.TripProposal, trip_id)
    user = flask_login.current_user

    if user not in trip.participants:
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    if user.is_editor_for(trip) and trip.num_editors() <= 1:
        flash("The last editor cannot leave the trip.", "error")
        return redirect(url_for("main.trip", trip_id=trip_id))
    
    user_participation = (
        db.session.query(model.TripProposalParticipation)
        .filter_by(user_id=user.id, trip_proposal_id=trip.id)
        .first()
    )
        
    db.session.delete(user_participation)
    db.session.commit()

    return redirect(url_for("main.trip", trip_id=trip_id))

@bp.route("/trip/<int:trip_id>/message", methods=["POST"])
@flask_login.login_required
def new_message(trip_id):
    user = flask_login.current_user
    content = request.form.get("message-content", "").strip()
    forum_topic = request.form.get("forum_topic", "Main").strip() #to get the specific channel/forum of the messages
    new_forum_topic = request.form.get("new_forum_topic", "").strip() #if user wants to make a new forum for some specific messages
    if new_forum_topic and new_forum_topic != "":
        forum_topic = new_forum_topic

    if not content:
        flash("Message cannot be empty", "error")
        return redirect(url_for("main.trip", trip_id=trip_id, forum_topic=forum_topic))
    
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

# referred to Claude for JSON logic
@bp.route('/trip/<int:trip_id>/meetups')
@flask_login.login_required
def trip_meetup_retrieval(trip_id):
    trip = model.TripProposal.query.get_or_404(trip_id)

    meetups = model.Meetup.query.filter_by(trip_proposal_id=trip_id).all()

    return jsonify([{
        'id': meetup.id,
        'title': meetup.location,
        'start': meetup.date_time.isoformat(),
        'description': meetup.description,
        'extendedProps': {
            'location': meetup.location,
            'description': meetup.description,
            'creator': meetup.creator.name,
            'link': meetup.link
        }
    } for meetup in meetups])

@bp.route('/trip/<int:trip_id>/meetups', methods=['POST'])
@flask_login.login_required
def new_trip_meetup(trip_id):
    current_user=flask_login.current_user
    trip = model.TripProposal.query.get_or_404(trip_id)

    json = request.get_json()

    try:
        date = json['date']
        time = json['time']
        datetime_string = f"{date} {time}"
        date_time = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')

        meetup = model.Meetup(
            trip_proposal_id=trip_id,
            creator_id=current_user.id,
            location=json['location'],
            date_time=date_time,
            description=json.get('description'),
            link=json.get('link')

        )

        db.session.add(meetup)
        db.session.commit()

        return jsonify({'success': True, 'id': meetup.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success':False, 'error': str(e)}), 400
    
@bp.route('/trip/<int:trip_id>/meetups/<int:meetup_id>', methods=['DELETE'])
@flask_login.login_required
def delete_meetup(trip_id, meetup_id):
    trip = model.TripProposal.query.get_or_404(trip_id)
    meetup = model.Meetup.query.get_or_404(meetup_id)

    try:
        db.session.delete(meetup)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@bp.route("/browse_trips")
@flask_login.login_required
def browse_trips():
    user = flask_login.current_user

    trips_query = model.TripProposal.query

    max_budget = request.args.get("max_budget", type=float)
    if max_budget:
        trips_query = trips_query.filter(model.TripProposal.budget <= max_budget)

    min_age = request.args.get("min_age", type=int)
    max_age = request.args.get("max_age", type=int)
    if min_age:
        trips_query = trips_query.filter(model.TripProposal.min_age >= min_age)
    if max_age:
        trips_query = trips_query.filter(model.TripProposal.max_age <= max_age)

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if start_date:
        trips_query = trips_query.filter(model.TripProposal.start_date >= start_date)
    if end_date:
        trips_query = trips_query.filter(model.TripProposal.end_date <= end_date)

    origin = request.args.get("origin")
    if origin:
        trips_query = trips_query.filter(model.TripProposal.origin.ilike(f"%{origin}%")) 
        #referenced ChatGPT for 'ilike', which compares with case insensitive values

    destination = request.args.get("destination")
    if destination:
        trips_query = trips_query.filter(model.TripProposal.destinations.ilike(f"%{destination}%"))

    university = request.args.get("university")
    if university:
       trips_query = trips_query.join(model.User, model.TripProposal.creator_id == model.User.id)

       trips_query = trips_query.filter(
        db.or_(
            # Trip is for user's home university
            db.and_(
                model.TripProposal.university == "home_uni",
                db.or_(
                    model.User.home_uni == user.home_uni,
                    model.User.visiting_uni == user.home_uni
                )
            ),
            # Trip is for user's visiting university
            db.and_(
                model.TripProposal.university == "visiting_uni",
                db.or_(
                    model.User.home_uni == user.visiting_uni,
                    model.User.visiting_uni == user.visiting_uni
                )
            ),
            # Trip is for both universities
            db.and_(
                model.TripProposal.university == "both",
                db.or_(
                    model.User.home_uni == user.home_uni,
                    model.User.visiting_uni == user.home_uni,
                    model.User.home_uni == user.visiting_uni,
                    model.User.visiting_uni == user.visiting_uni
                )
            )
        )
    )
    
    status = request.args.get("status")
    if status:
        status_map = {
            "OPEN" : model.TripProposalStatus.OPEN.value,
            "APPROVAL_REQUIRED" : model.TripProposalStatus.APPROVAL_REQUIRED.value, # type: ignore
            "CLOSED" : model.TripProposalStatus.CLOSED.value, # type: ignore
            "FINALIZED" : model.TripProposalStatus.FINALIZED.value, # type: ignore
            "CANCELLED" : model.TripProposalStatus.CANCELLED.value, # type: ignore
        }

        status_value = status_map.get(status)
        if status_value:
            trips_query = trips_query.filter(model.TripProposal.status == status_value)

    trips = trips_query.order_by(model.TripProposal.timestamp.desc()).all()

    return render_template("main/browse_trips.html", trips=trips)
