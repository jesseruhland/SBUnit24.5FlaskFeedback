from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    """form for new user registrations"""

    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30, message="First Name cannot exceed 30 characters.")])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30, message="Last Name cannot exceed 30 characters.")])
    email = StringField("Email Address", validators=[InputRequired(), Email(), Length(max=50, message="Email Address cannot exceed 50 characters.")])
    username = StringField("Username", validators=[InputRequired(), Length(max=20, message="Username cannot exceed 20 characters.")])
    password = StringField("Password", validators=[InputRequired(), Length(min=8, message="Password must be at least 8 characters.")])

class LoginForm(FlaskForm):
    """form for existing users to access private content"""

    username = StringField("Username", validators=[InputRequired(), Length(max=20, message="Username cannot exceed 20 characters.")])
    password = StringField("Password", validators=[InputRequired(), Length(min=8, message="Password must be at least 8 characters.")])

