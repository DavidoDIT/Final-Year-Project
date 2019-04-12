""" This file is a models file. It uses SQLAlchemy to communicate with the database """
from winesite import db, login_manager
from datetime import datetime
from flask_login import UserMixin

""" Flask has great modules such flask-login that help a lot with development """


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" First class in the models file is the user, this sets all of the tables attributes and links a relation to 
    the reviews """


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    reviews = db.relationship("Review", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"


""" This class in the models table is the review table, this sets all the attributes for a review and links the
    relationship to the user table """


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    variety = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.Integer(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Review('{self.title}','{self.date_posted}','{self.variety}','{self.rating}')"
