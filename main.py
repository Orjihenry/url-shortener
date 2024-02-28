import random
import string

from flask import Flask, render_template
from flask_login import UserMixin
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config.from_object(app_config)
db = SQLAlchemy(app)


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


def generate_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
