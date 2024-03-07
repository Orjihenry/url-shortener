import random
import string
import secrets
import hashlib

from flask import Flask, render_template, flash, session, url_for, redirect
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from config import app_config
from flask_sqlalchemy import SQLAlchemy
from webforms import RegForm, UrlForm, LoginForm
from datetime import datetime


app = Flask(__name__)

app.config.from_object(app_config)
db = SQLAlchemy(app)
salt = secrets.token_hex(16)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'


# Url db model
class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(225), nullable=False)
    short_url = db.Column(db.String(225), nullable=False, unique=True)
    url_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    custom_url = db.Column(db.String(15))
    visits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Urls {self.short_url}>'


# User db model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225), nullable=False)
    email = db.Column(db.String(225), nullable=False, unique=True)
    password_hash = db.Column(db.String(225))
    salt = db.Column(db.String(32))
    user_urls = db.relationship('Urls', backref='poster')
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)


# User Registration
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

            flash('User Registered Successfully', 'error')
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('index'))
        elif user is not None:
            flash('Email already exists!', 'error')
    return render_template("register.html", form=form, flash=flash)


# User Login
@app.route("/login", methods=['GET', 'POST'])
def user_login():
    """
        User Login
    :return:
    """
    email = None
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and verify_password(form.password.data, user.password_hash, user.salt):
            flash('Login Successful', 'error')

            # Set user session
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('index'))  # Redirect to a dashboard route
        else:
            flash('Invalid email or password', 'error')

    return render_template("login.html", form=form, flash=flash)


# User loader
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


# Logout function
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logout Successful!', 'error')
    return redirect(url_for('user_login'))


# Verify password
def verify_password(password, password_hash, salt):
    """
        Verify if password is EqualTo hashed password in db
        :param password:
        :param password_hash:
        :param salt:
        :return:
    """
    hashed_pass = (password + salt).encode('utf-8')
    computed_hash = hashlib.sha256(hashed_pass).hexdigest()
    return computed_hash == password_hash


# Generate random string for short url
def generate_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


# Index route & Shorten URL
@app.route("/", methods=["GET", "POST"])
def index():
    form = UrlForm()
    short_url = None
    long_url = None
    custom_url = None
    url_visits = session.get(Urls.visits)
    url_user_id = session.get('user_id')

    # Check if user is logged in
    if url_user_id:
        if form.validate_on_submit():
            short_url = generate_url()
            store_urls = Urls.query.filter_by(short_url=form.short_url.data).first()

            # Check if custom_url is not empty
            if form.custom_url.data:
                joined = form.custom_url.data.split()
                custom_url = '-'.join(joined[0:])

                try:
                    db_check = Urls.query.filter_by(custom_url=custom_url).first()
                    if db_check:
                        flash('Alias is not available. Please choose a different one.', 'error')

                    if custom_url:
                        short_url = custom_url

                    if store_urls is None:
                        store_urls = Urls(
                            long_url=form.long_url.data,
                            short_url=short_url,
                            url_user_id=url_user_id,
                            custom_url=form.custom_url.data
                        )
                        db.session.add(store_urls)
                        db.session.commit()
                except IntegrityError as e:
                    db.session.rollback()
                    # flash('Error: Alias is not available. Please choose a different one.', 'error')
                    short_url = ''
            else:
                # If custom_url is empty, generate short URL without custom alias
                if store_urls is None:
                    store_urls = Urls(
                        long_url=form.long_url.data,
                        short_url=short_url,
                        url_user_id=url_user_id
                    )
                    db.session.add(store_urls)
                    db.session.commit()

    else:
        # If user is not logged in, generate short URL without custom alias
        if form.validate_on_submit():
            short_url = generate_url()
            store_urls = Urls.query.filter_by(short_url=form.short_url.data).first()

            # Check if short_url exists in db
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


# Redirects to long url
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
        return render_template('404.html')


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# Run app
if __name__ == "__main__":
    app.run(debug=True)
