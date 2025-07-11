import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, flash, session, url_for, redirect
from flask_login import (UserMixin, login_user, LoginManager, login_required, logout_user, current_user )
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from webforms import ChangePasswordForm, RegForm, UrlForm, LoginForm, UpdateForm, DeleteForm, DeleteUserForm
from datetime import datetime
from generate_qr import generate_qr_code


app = Flask(__name__)

app.config.from_object(app_config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    first_name = db.Column(db.String(225), nullable=False)
    last_name = db.Column(db.String(225), nullable=False)
    email = db.Column(db.String(225), nullable=False, unique=True)
    password_hash = db.Column(db.String(225))
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
    User registration: Creates a new user with hashed password
    """
    form = RegForm()

    if form.validate_on_submit():
        # Checks if email is already taken
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash password using Werkzeug
            hashed_password = generate_password_hash(form.password_hash.data, method='pbkdf2')
            user = Users(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password_hash=hashed_password
            )

            db.session.add(user)
            db.session.commit()

            flash('User Registered Successfully', 'success')
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('index'))
        else:
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
        if user and check_password_hash(user.password_hash, form.password.data):
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


# User Profile
@app.route('/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    update_user_form = UpdateForm()
    if update_user_form.validate_on_submit():
        current_user.first_name = update_user_form.first_name.data
        current_user.last_name = update_user_form.last_name.data
        current_user.email = update_user_form.email.data
        db.session.add(current_user)
        db.session.commit()
        flash('User Updated Successfully', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('User Update Failed', 'error')
    return redirect(url_for('dashboard'))


# Change Password
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():

        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('change_password'))
        
        new_hashed_password = generate_password_hash(form.password_hash.data, method='pbkdf2')
        current_user.password_hash = new_hashed_password

        db.session.commit()
        flash('Password changed successfully.', 'success')

    return redirect(url_for('dashboard'))


@app.route("/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    delete_user_form = DeleteUserForm()

    if current_user.id != user_id:
        flash("You can only delete your own account.", "error")
        return redirect(url_for("dashboard"))

    user = Users.query.get_or_404(user_id)

    if delete_user_form.validate_on_submit():
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been deleted.", "success")
        return redirect(url_for("user_login"))

    flash("Deletion failed. Please try again.", "error")
    return redirect(url_for("dashboard"))


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    update_user_form = UpdateForm()
    change_password_form = ChangePasswordForm()
    delete_url_form = DeleteForm()
    delete_user_form = DeleteUserForm()
    return render_template('dashboard.html',
                           user=current_user,
                           update_user_form=update_user_form,
                           change_password_form=change_password_form,
                           delete_url_form=delete_url_form,
                           delete_user_form=delete_user_form
                           )


# Logout function
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logout Successful!', 'error')
    return redirect(url_for('user_login'))


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
            store_urls = Urls.query.filter_by(
                short_url=form.short_url.data).first()

            # Check if custom_url is not empty
            if form.custom_url.data:
                joined = form.custom_url.data.split()
                custom_url = '-'.join(joined[0:])

                try:
                    db_check = Urls.query.filter_by(
                        custom_url=custom_url).first()
                    if db_check:
                        flash('Alias is not available. \
                              Please choose a different one.',
                              'error'
                              )

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
                    short_url = ''
            else:
                """
                    If custom_url is empty,
                    generate short URL without custom alias
                """
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
            store_urls = Urls.query.filter_by(
                short_url=form.short_url.data).first()

            # Check if short_url exists in db
            if store_urls is None:
                store_urls = Urls(long_url=form.long_url.data,
                                  short_url=short_url
                                  )
                db.session.add(store_urls)
                db.session.commit()

                full_short_url = request.url_root + short_url
                generate_qr_code(full_short_url, short_url, logo_path='static/logo.png')

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


# delete URL records
@app.route("/delete/<short_url>", methods=["POST"])
@login_required
def delete_url_record(short_url):
    delete_url_form = DeleteForm()
    """
        Deletes short URL record from the db.
        Only accessible to the logged-in user who created it.
        :param short_url:
        :return:
    """
    if delete_url_form.validate_on_submit:
        url_entry = Urls.query.filter_by(short_url=short_url).first()

        if url_entry and url_entry.url_user_id == current_user.id:
            db.session.delete(url_entry)
            db.session.commit()
            flash("URL record deleted successfully.", "success")
        else:
            flash("You do not have permission to delete this URL.", "error")

    return redirect(url_for("dashboard"))


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
