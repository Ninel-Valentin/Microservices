from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, UserMixin, LoginManager
from wtforms import *
from sqlalchemy import *

from microskel.db_module import Base
import datetime

from decouple import config
from requests import delete as Delete
from requests import get as Get
from requests import post as Post
from requests import put as Put

req_mapping = {"GET": Get, "PUT": Put, "POST": Post, "DELETE": Delete}

events_url = config("EVENTS_SERVICE_URL")
weather_url = config("WEATHER_SERVICE_URL")


def proxy_request(request, target_url):
    req = req_mapping[request.method]
    kwargs = {"url": target_url, "params": request.args}
    if request.method in ["PUT", "POST"]:
        kwargs["data"] = dict(request.form)
    response = req(**kwargs).json()
    return json.dumps(response)


from functools import wraps


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            return redirect(url_for(endpoint="login", next_url=request.url))

    return wrapper


class LoginForm(Form):
    def check_existing(form, field):
        existing = session.query(User).filter(User.email == field.data).first()
        if not existing:
            raise ValidationError("Email is not present in the system")

    email = StringField(
        "Email / User",
        validators=[
            validators.DataRequired(message="Email / User is required!"),
            # check_existing, # can be implemented custom functions
            validators.Email(message="Invalid email"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[validators.DataRequired(message="Password is required!")],
    )


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=true)
    email = Column(String(128))
    password = Column(String(128))
    name = Column(String(256))


class LoginUser(UserMixin):
    def __init__(self, id):
        self.id = id


def authenticate(email, password):
    if not email or not password:
        return False
    result = session.query(User).filter(User.email == email).first()
    return result is not None and result.password == password


def configure_views(app):
    @app.route("/citybreak", methods=["GET"])
    def get():
        city = request.args.get("city")
        date = request.args.get("date", str(datetime.date.today()))
        if not city or not date:
            return "Invalid request: city or date are missing", 400
        print(f"EVENTS_URL = {events_url}?city={city}&date={date}")
        print(f"WEATHER_ULR = {weather_url}?city={city}&date={date}")
        events = Get(f"{events_url}?city={city}&date={date}", verify=False).json()
        weather = Get(f"{weather_url}?city={city}&date={date}", verify=False).json()
        return {"events": events, "weather": weather}, 200

    @app.route("/add_user")
    def add_user(db: SQLAlchemy):
        user = User(email="george_spadasinu@yahoo.com", password="abc123", name="Gică")
        db.session.add(user)
        db.session.commit()
        return "User added", 200

    @app.route("/login", methods=["GET", "POST"])
    def login():
        next_url = request.args.get("next_url", "/index")
        # if not is_safe_url(next_url):
        #     return abort(400) # Bad request

        form = LoginForm(request.form)
        if request.method == "POST" and form.validate():
            email = form.email.data
            password = form.password.data
            auth = authenticate(email, password)
            if not auth:  # TBD
                app.logger.error(f"Login failed for: {email} and {password}")
                form.password.errors = ["Incorrect email or passord"]
                return render_template("login.html", form=form, next=next_url)
            else:
                app.logger.info(f"Login successful for: {email}")
                login_user(
                    LoginUser(email),
                    duration=datetime.timedelta(days=30),
                    remember=True,
                )
                session["logged_in"] = True
                # user = db.session.query(User).filter(User.email==email).first()
                return redirect(next_url or url_for("index"))
        else:
            return render_template("login.html", form=form, next=next_url)

    @login_required
    @app.route("/events", methods=["GET", "POST", "PUT", "DELETE"])
    def events():
        return proxy_request(request, events_url)

    @login_required
    @app.route("/weather", methods=["GET", "POST", "PUT", "DELETE"])
    def weather():
        return proxy_request(request, weather_url)


if __name__ == "__main__":
    server = app.server
    login_manager = LoginManager()
    login_manager.init_app(server)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
