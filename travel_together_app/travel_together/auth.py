from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import flask_login

from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from . import model
from travel_together.constants import COUNTRIES, COUNTRY_NAMES, UNIVERSITIES, COUNTRY_OF_UNIVERSITIES

bp = Blueprint("auth", __name__)


@bp.route("/signup")
def signup():
    return render_template(
        "auth/signup.html", 
        countries=COUNTRIES,
        country_names=COUNTRY_NAMES,
        universities=UNIVERSITIES,
        country_of_universities=COUNTRY_OF_UNIVERSITIES
    )

@bp.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    username = request.form.get("username")
    country = request.form.get("country")
    home_uni = request.form.get("home_uni")
    birthday = request.form.get("birthday")
    password = request.form.get("password")
    # Check that passwords are equal
    if password != request.form.get("password_repeat"):
        flash("Sorry, passwords are different")
        return redirect(url_for("auth.signup"))
    # Check if the email is already at the database
    query = db.select(model.User).where(model.User.email == email)
    user = db.session.execute(query).scalar_one_or_none()
    if user:
        flash("Sorry, the email you provided is already registered")
        return redirect(url_for("auth.signup"))
    
    # Moved to another step of signup, not needed here for now
    # new_user = model.User(email=email, name=username, password=password_hash)
    # db.session.add(new_user)
    # db.session.commit()

    session["signup_data"] = {
        "email": email,
        "username": username,
        "password_hash": generate_password_hash(password)
    }

    return redirect(url_for("auth.singup2"))

@bp.route("/signup2")
def singup2():
    signup_data = session.get("signup_data")
    if not signup_data:
        return redirect(url_for("auth.signup"))
    return render_template("auth/signup2.html")

@bp.route("/signup2", methods=["POST"])
def signup2_post():
    signup_data = session.get("signup_data")
    if not signup_data:
        flash("Session expired. Please start the signup process again.")
        return redirect(url_for("auth.signup"))

    description = request.form.get("description") or "User has not provided a description."
    birthday = request.form.get("birthday")
    home_uni = request.form.get("home_uni")
    visiting_uni = request.form.get("visiting_uni")
    country = request.form.get("country")

    # Create new user with all collected data
    new_user = model.User(
        email=signup_data["email"],
        name=signup_data["username"],
        password=signup_data["password_hash"],
        desc=description,
        birthday=birthday,
        home_uni=home_uni,
        visiting_uni=visiting_uni,
        country=country
    )
    db.session.add(new_user)
    db.session.commit()

    # Clear session data
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
        flash("Login successful!")
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
