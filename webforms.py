from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo


# User Registration Form
class RegForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password",
                                  validators=[DataRequired(),
                                              EqualTo("password_hash2",
                                                      message="Passwords Must Match!")
                                              ]
                                  )
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


# User Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Update User Form
class UpdateForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Change Password Form
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    password_hash = PasswordField("New Password",
                                  validators=[DataRequired(),
                                              EqualTo("password_hash2",
                                                      message="Passwords Must Match!")
                                              ]
                                  )
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


# URL Shortener Form
class UrlForm(FlaskForm):
    long_url = StringField("Enter URL", validators=[DataRequired()])
    short_url = StringField("Generated Short URL")
    custom_url = StringField("Enter Custom URL Alias")
    submit = SubmitField('Submit')
