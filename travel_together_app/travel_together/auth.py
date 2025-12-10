import os
from datetime import datetime
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
import flask_login

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from . import db
from . import model
from travel_together.constants import COUNTRIES, COUNTRY_NAMES, UNIVERSITIES, COUNTRY_OF_UNIVERSITIES, MAX_DESC_LENGTH

bp = Blueprint("auth", __name__)

@bp.route("/signup", methods=["GET"])
def signup():
    return render_template(
        "auth/signup.html",
        countries=COUNTRIES,
        universities=UNIVERSITIES
    )

@bp.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    password_repeat = request.form.get("password_repeat")

    if password != password_repeat:
        flash("Sorry, passwords are different")
        return redirect(url_for("auth.signup"))

    query = db.select(model.User).where(model.User.email == email)
    user = db.session.execute(query).scalar_one_or_none()
    if user:
        flash("Sorry, the email you provided is already registered")
        return redirect(url_for("auth.signup"))

    session["signup_data"] = {
        "email": email,
        "username": username,
        "password_hash": generate_password_hash(password),
        "profile_pic": "Defaultpfp.png"
    }

    return redirect(url_for("auth.signup2"))


@bp.route("/signup2")
def signup2():
    signup_data = session.get("signup_data")
    if not signup_data:
        return redirect(url_for("auth.signup"))
    return render_template(
        "auth/signup2.html",
        countries=COUNTRIES,
        universities=UNIVERSITIES
    )


@bp.route("/signup2", methods=["POST"])
def signup2_post():
    signup_data = session.get("signup_data")
    if not signup_data:
        return redirect(url_for("auth.signup"))

    profile_pic = request.files.get("profile_pic")
    if profile_pic and profile_pic.filename != "":
        filename = secure_filename(profile_pic.filename)
        save_path = os.path.join(current_app.static_folder, "resources", filename)
        profile_pic.save(save_path)
    else:
        filename = signup_data["profile_pic"]
        
    desc = request.form.get("description") or ""
    
    if desc and len(desc) > MAX_DESC_LENGTH:
        flash(f"Maximum description length is {MAX_DESC_LENGTH} characters.")
        return redirect(url_for("auth.signup2"))
    
    birthday = request.form.get("birthday")
    birthday = datetime.strptime(birthday, "%Y-%m-%d").date() if birthday else None
    if birthday and birthday > datetime.now().date():
        flash("Provided birthday is invalid.")
        return redirect(url_for("auth.signup2"))
    
    home_uni=request.form.get("home_uni")
    visiting_uni=request.form.get("visiting_uni")
    
    if home_uni and visiting_uni and home_uni == visiting_uni:
        flash("Home and visiting universities must be different.")
        return redirect(url_for("auth.signup2"))
    
    new_user = model.User(
        email=signup_data["email"],
        name=signup_data["username"],
        password=signup_data["password_hash"],
        desc=desc,
        birthday=birthday,
        home_uni=home_uni,
        visiting_uni=visiting_uni,
        country=request.form.get("country"),
        profile_pic=filename
    )

    db.session.add(new_user)
    db.session.commit()

    session.pop("signup_data", None)
    flash("Signup successful! Please log in.")
    return redirect(url_for("auth.login"))


@bp.route("/login")
def login():
    return render_template("auth/login.html")

@bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    # Check if the email is already at the database
    query = db.select(model.User).where(model.User.email == email)
    user = db.session.execute(query).scalar_one_or_none()
    if user and check_password_hash(user.password, password):
        flask_login.login_user(user)
        return redirect(url_for("main.index"))
    else:
        flash("Wrong email and/or password. Please try again.")
        return redirect(url_for("auth.login"))

@bp.route("/logout", methods=["GET"])
@flask_login.login_required
def logout_post():
    flask_login.logout_user()
    return redirect(url_for("auth.login"))

@bp.route("/edit-profile")
@flask_login.login_required
def edit_profile():
    return render_template(
        "main/edit_profile.html",
        countries=COUNTRIES,
        universities=UNIVERSITIES
    )

@bp.route("/edit-profile", methods=['POST'])
@flask_login.login_required
def edit_profile_post():
    user = flask_login.current_user

    birthday = request.form.get('birthday')
    if birthday:
        birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
        
        if birthday > datetime.now().date():
            flash("Provided birthday is invalid.")
            return redirect(url_for("auth.edit_profile"))
        
        user.birthday = birthday
    
    country = request.form.get('country')
    if country:
        user.country = country

    desc = request.form.get('description')
    if desc and len(desc) > MAX_DESC_LENGTH:
        flash(f"Maximum description length is {MAX_DESC_LENGTH} characters.")
        return redirect(url_for("auth.edit_profile"))
    
    user.desc = desc or user.desc

    # Optional home and visiting uni, otherwise stick to the old ones
    home_uni = request.form.get('home_uni')
    visiting_uni = request.form.get('visiting_uni')
    
    if home_uni:
        user.home_uni = home_uni
    if visiting_uni:
        user.visiting_uni = visiting_uni
    #profile pic requires specific handling, and is optional
    #referenced ChatGPT for help
    profile_pic = request.files.get('profile_pic')
    if profile_pic and profile_pic.filename != "":
            filename = secure_filename(profile_pic.filename)
            save_path = os.path.join(current_app.static_folder, "resources", filename)
            profile_pic.save(save_path)
            user.profile_pic = filename

    db.session.commit()
    flash("Profile updated.")

    return redirect(url_for('main.profile', user_id = user.id))
