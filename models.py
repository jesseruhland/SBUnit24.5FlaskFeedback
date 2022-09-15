"""Models for Feedback app"""

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    def __repr__(self) =
        """Display user information"""
        u = self
        return f"<User username:{u.username} / {u.first_name} {u.last_name}>"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), unique=True, nullable=False)
    last_name = db.Column(db.String(30), unique=True, nullable=False)

    feedbacks = db.relationship('Feedback', backref="users", cascade="all, delete")

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register a new User with a hashed password"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """Verify a user's credentials"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        
        else:
            return False

class Feedback(db.Model):
    """Feedback"""

    __tablename__ = "feedbacks"

    def __repr__(self) =
        """Display feeback and user information"""
        f = self
        return f"<Feedback title:{f.title} / username:{f.username}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey("users.username", ondelete="CASCADE"))
