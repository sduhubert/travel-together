# Things to import at the beginning
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Declarations to insert before the create_app function:
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

def create_app(test_config=None):

    app = Flask(__name__)

    # A secret for signing session cookies
    app.config["SECRET_KEY"] = "93220d9b340cf9a6c39bac99cce7daf220167498f91fa"


    app.config[
        "SQLALCHEMY_DATABASE_URI"
    # ] = "mysql+pymysql://adam:Tq6qlpko@localhost/travel_together"
    # Code to place inside create_app, after the other app.config assignment
    # app.config[
    #     "SQLALCHEMY_DATABASE_URI"
    # #] = "mysql+pymysql://traveltogether:waDBlog@localhost/TravelTogether"
    ] = "mysql+pymysql://26_webapp_00:Tq6qlpko@mysql.lab.it.uc3m.es/26_webapp_00b"
    
    # app.config[
    #   "SQLALCHEMY_DATABASE_URI"
    # ] = "mysql+pymysql://26_webapp_33:lJuqOOoe@mysql.lab.it.uc3m.es/26_webapp_33a"

    #app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///microblog.db"

    db.init_app(app)

    # Register blueprints
    # (we import main from here to avoid circular imports in the next lab)
    from . import main, auth

        # Inside create_app:
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from . import model

    @login_manager.user_loader
    def load_user(user_id):
      return db.session.get(model.User, int(user_id))
    
    # Jinja filter for getting time ago
    def time_ago(dt):
        now = datetime.utcnow()
        diff = now - dt
        seconds = diff.total_seconds()

        intervals = (
            ('year', 60*60*24*365),
            ('month', 60*60*24*30),
            ('day', 60*60*24),
            ('hour', 60*60),
            ('minute', 60),
            ('second', 1),
        )

        for name, count in intervals:
            value = int(seconds // count)
            if value > 0:
                return f"{value} {name}{'s' if value != 1 else ''} ago"
        return "just now"

    app.jinja_env.filters['time_ago'] = time_ago

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    return app
