"""Flask Feedback application."""

from flask import Flask, request, redirect, render_template, flash
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, LoginForm

# from forms import PetForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretkey'

# debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route("/")
def redirect_to_register():
    """Redirect user to /register - per assignment directions"""
    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def create_user():
    """on GET - display registration form.
    on POST - process new user registration.
    """

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()
        session["username"] = new_user.username
        flash(f"Welcome to the FeedbackApp, {new_user.first_name}", "success")
        return redirect("/secret")
    
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def log_user_in():
    """on GET - display login form.
    on POST - process the login form
    """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            return redirect("/secret")
        
        else:
            form.username.errors=["Invalid login.  Please try again."]

    return render_template("login.html", form=form)

@app.route("/secret")
def get_secret_page():
    return "You made it!"

