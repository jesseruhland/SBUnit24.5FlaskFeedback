"""Flask Feedback application."""

from flask import Flask, request, redirect, render_template, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
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
def show_feedback():
    """Show 10 most recent feedback posts"""
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).limit(10).all()
    return render_template("homepage.html", feedbacks=feedbacks)

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
        return redirect(f"/users/{new_user.username}")
    
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
            return redirect(f"/users/{user.username}")
        
        else:
            form.username.errors=["Invalid login.  Please try again."]

    return render_template("login.html", form=form)

@app.route("/users/<username>")
def display_user_page(username):
    """Page hidden to users who are not logged in"""

    if "username" not in session:
        flash("You must be logged in to view this page!", "warning")
        return redirect("/login")

    user = User.query.get_or_404(username)

    return render_template("user-detail.html", user=user)

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """Remove a user from the database if they are the logged-in user"""

    if "username" not in session:
        flash("You must be logged in to view this page!", "warning")
        return redirect("/login")
    
    if username == session['username']:
        user = User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        flash(f"User has successfully been deleted!", "success")
        return redirect("/")
    
    else:
        flash(f"You do not have permission to do that!", "danger")
        return redirect("/")


@app.route("/logout", methods=["POST"])
def logout_user():
    """Log out current user, redirect to homepage."""

    session.pop("username")

    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def add_user_feedback(username):
    """on GET - display feedback form.
    on POST - process new feedback submission.
    """
    if "username" not in session:
        flash("You must be logged in to view this page!", "warning")
        return redirect("/login")

    if username == session['username']:
        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            username = username

            new_feedback = Feedback(title=title, content=content, username=username)

            db.session.add(new_feedback)
            db.session.commit()
          
            flash(f"Feedback has been saved!", "success")
            return redirect(f"/users/{username}")
        
        return render_template("feedback-form.html", form=form)
    
    flash(f'You cannot share feedback as {username} if you are not logged in to that account!', 'danger')
    return redirect("/")

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
def updated_feedback(feedback_id):
    """on GET - display feedback form.
    on POST - process updated feedback submission.
    """
    if "username" not in session:
        flash("You must be logged in to view this page!", "warning")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.username == session['username']:
        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()
          
            flash(f"Feedback has been updated!", "success")
            return redirect(f"/users/{feedback.username}")
        
        return render_template("feedback-form.html", form=form)
    
    flash(f"You cannot edit {feedback.username}'s feedback if you are not logged in to that account!", 'danger')
    return redirect("/")

@app.route("/feedback/<int:feedback_id>/delete", methods=['POST'])
def delete_feedback(feedback_id):
    """on POST - process feedback deletion."""

    if "username" not in session:
        flash("You must be logged in to view this page!", "warning")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.username == session['username']:
        
        db.session.delete(feedback)
        db.session.commit()
        flash(f"'{feedback.title}' has successfully been deleted!", "success")
        return redirect(f"/users/{feedback.username}")
    
    flash(f"You cannot delete {feedback.username}'s feedback if you are not logged in to that account!", 'danger')
    return redirect("/")