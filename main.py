import random
import string
import secrets
import hashlib

from flask import Flask, render_template, flash, session, url_for, redirect
from flask_login import UserMixin, login_user
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from webforms import RegForm, UrlForm
from datetime import datetime


app = Flask(__name__)

app.config.from_object(app_config)
db = SQLAlchemy(app)
salt = secrets.token_hex(16)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(225), nullable=False)
    short_url = db.Column(db.String(225), nullable=False, unique=True)
    url_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    custom_url = db.Column(db.String(15), unique=True)
    visits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Urls {self.short_url}>'


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225), nullable=False)
    email = db.Column(db.String(225), nullable=False, unique=True)
    password_hash = db.Column(db.String(225))
    salt = db.Column(db.String(32))
    user_urls = db.relationship('Urls', backref='poster')
    date = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/register", methods=['GET', 'POST'])
def reg_user():
    """
        User registration: Uses flask.session to store users
    """
    email = None
    form = RegForm()

    if form.validate_on_submit():
        # Checks if email is already taken
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash password using hashlib & secrets
            hashed_pass = form.password_hash.data + salt
            password = hashlib.sha256(hashed_pass.encode()).hexdigest()
            user = Users(name=form.name.data,
                         email=form.email.data,
                         password_hash=password,
                         salt=salt
                         )
            db.session.add(user)
            db.session.commit()

            flash('User Registered Successfully')
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('index'))
        elif user is not None:
            flash('Email already exists!')
    return render_template("register.html", form=form, flash=flash)


def generate_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


@app.route("/", methods=["GET", "POST"])
def index():
    """
        Renders URL generation form
    :return:
    """
    form = UrlForm()
    short_url = None
    long_url = None
    custom_url = None
    url_visits = session.get(Urls.visits)
    url_user_id = session.get('user_id')

    if url_user_id:
        """
            Renders shortened urls generation form
            With custom short_url if user is registered.
        """
        if form.validate_on_submit():
            short_url = generate_url()
            store_urls = Urls.query.filter_by(short_url=form.short_url.data).first()

            custom_url = form.custom_url.data

            if custom_url:
                short_url = custom_url

            if store_urls is None:
                store_urls = Urls(long_url=form.long_url.data,
                                  short_url=short_url,
                                  custom_url=form.custom_url.data
                                  )
                db.session.add(store_urls)
                db.session.commit()
    else:
        """
            Renders shortened urls generation form
            Without custom short_url if user is not registered.
        """
        if form.validate_on_submit():
            short_url = generate_url()
            store_urls = Urls.query.filter_by(short_url=form.short_url.data).first()

            if store_urls is None:
                store_urls = Urls(long_url=form.long_url.data, short_url=short_url)
                db.session.add(store_urls)
                db.session.commit()

    return render_template("index.html",
                           form=form,
                           short_url=short_url,
                           long_url=long_url,
                           custom_url=custom_url,
                           visits=url_visits
                           )


@app.route("/<short_url>")
def redirect_url(short_url):
    """
        Redirects short urls to long urls.
        Calculates and stores visitors to short url
    :param short_url:
    :return:
    """
    url_entry = Urls.query.filter_by(short_url=short_url).first()
    if url_entry:

        url_entry.visits += 1

        db.session.commit()

        return redirect(url_entry.long_url)
    else:
        return "URL NOT FOUND", 404


if __name__ == "__main__":
    app.run(debug=True)
