"""Flask Feedback application."""

from flask import Flask, request, redirect, render_template, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

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
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('That username is already in use. Please choose another.')
            return render_template("register.html", form=form)
        session["username"] = new_user.username
        flash(f"Welcome to the FeedbackApp, {new_user.first_name}!", "success")
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
            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect("/secret")
        
        else:
            form.username.errors=["Invalid login.  Please try again."]

    return render_template("login.html", form=form)

@app.route("/secret")
def get_secret_page():
    """Page hidden to users who are not logged in"""

    if "username" not in session:
        flash("You must be logged in to view this page!")
        return redirect("/")

    return "You made it!"

@app.route("/logout", methods=["POST"])
def logout_user():
    """Log out current user, redirect to homepage."""

    session.pop("username")

    return redirect("/")



