from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    password_hash = generate_password_hash(password)
    # TODO: Fix home_uni selection in the signup form
    new_user = model.User(email=email, name=username, password=password_hash, birthday=birthday, country=country, home_uni=home_uni)
    db.session.add(new_user)
    db.session.commit()
    flash("You've successfully signed up!")
    return redirect(url_for("main.index"))

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
