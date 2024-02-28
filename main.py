import random
import string
import secrets
import hashlib

from flask import Flask, render_template, flash, session, url_for, redirect
from flask_login import UserMixin, login_user
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from webforms import RegForm
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
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
