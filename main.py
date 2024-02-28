from flask import Flask, render_template
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


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
