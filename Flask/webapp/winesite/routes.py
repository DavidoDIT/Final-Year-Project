"""This file is the routes of the project which uses API Restfull calls."""
from flask import render_template, url_for, flash, redirect, request, abort
from winesite.forms import Register, Login, PredictData, AccountUpdate, ReviewForm
from winesite.models import User, Review
from winesite import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import tensorflow as tf
from tensorflow import keras
import pickle
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import secrets
import os
from PIL import Image

"""Firstly this function opens the tokenizer used in our prediction function. This allows the users input to be 
    tokenized with the same tokenizer that was used while developing the model"""

with open("winesite/h5models/tokenizer.pickle", "rb") as handle:
    tokenize = pickle.load(handle)

"""This route is the home page route, This shows all of the user reviews, uses pagination to only keep 5 reviews per
    page and also sends data to the deep model function which takes the users inputs from the predict form and runs it
    through the model to generate a prediction"""


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    page = request.args.get("page", 1, type=int)
    reviews = Review.query.order_by(Review.date_posted.desc()).paginate(
        page=page, per_page=5
    )
    form = PredictData()
    if form.validate_on_submit():
        input_one = form.description.data
        input_two = form.variety.data
        input_three = form.country.data
        """Users inputs to the form are take and inputted into a dataframe, the variable df is made global to be used 
        in another function"""
        global df
        df = pd.DataFrame(
            data=[[input_one, input_two, input_three]],
            columns=["description", "variety", "country"],
        )
        return redirect(url_for("predict"))
    return render_template("home.html", reviews=reviews, form=form)


"""This route is the predict route, this is where the users input data gets transformed and processed to be ran through 
    the deep model"""


@app.route("/predict", methods=["GET"])
def predict():
    """The dataframe from the previous function is take and the inputs are removed"""
    input_one = df["description"]
    input_two = df["variety"]
    input_three = df["country"]
    """The tokeinzer from the beginning of the file is used witht the description input (input_one) then bag of words
        is implemented"""
    tokenize.fit_on_texts(input_one)
    input_one_bow = tokenize.texts_to_matrix(input_one)
    """The variety and country are put through the encoder to be encoded and then one-hot encoded. The num classes is
        defined so that the inputs hae the same shape as the deep model"""
    encoder = LabelEncoder()
    encoder.fit(input_two)
    input_two = encoder.transform(input_two)
    num_classes = 33
    encoder.fit(input_three)
    input_three = encoder.transform(input_three)
    num_classes_1 = 12
    input_two = keras.utils.to_categorical(input_two, num_classes)
    input_three = keras.utils.to_categorical(input_three, num_classes_1)
    """The description input is then used with the keras word embedding and the three inputs and made into an input
        variable"""
    input_one_embedded = tokenize.texts_to_sequences(input_one)
    max_seq_length = 170
    input_one_embedded = keras.preprocessing.sequence.pad_sequences(
        input_one_embedded, maxlen=max_seq_length, padding="post"
    )
    input = [input_one_bow, input_two, input_three] + [input_one_embedded]
    """The graph variable is made global and the model.h5 file is loaded into the application, the graph is defined and
        the models weights are called. The rest of the graph function is called and the inputs are put onto the model to
        be used to return a prediction"""
    global graph
    model = tf.keras.models.load_model("winesite/h5models/test_model.h5")
    graph = tf.get_default_graph()
    model.get_weights()
    with graph.as_default():
        prediction = model.predict(input)
        prediction = prediction.round(2)
        """The prediction is in the format of a numpy array so it must be changed to a string and then the predict page
            is called"""
        retval = np.array2string(prediction, separator=",")
        print(retval)
    return render_template("predict.html", title="Prediction", prediction=retval)


""" This route allows a user to register, if a user is authenticated they will be redirected to the home page"""


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = Register()
    if form.validate_on_submit():

        """ As of Python 3, when you use bcrypt password hash you must use .decode, it would not be necesary if using 
            Python 2"""
        password_hash = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=password_hash
        )
        """if a users details areok they will be added and commited to the database then redirected to the login page"""
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}! Please log in!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


"""This route is the login route, ifa user is authenticated they will be redirected to the home page, if user submits
    details they will be queried against the database and their password hash checked"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            """flask-login module allows us to easily login users"""
            login_user(user)
            next_page = request.args.get("next")
            """This is a Turnary condtional which will bring the user to their original page destination or else to the
                        home page"""
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unusucessful Please check credentials", "danger")
    return render_template("login.html", title="Login", form=form)


"""This route logs out a user"""


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


""" Needs comment """


def new_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/", "profilephotos", picture_fn)

    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn


"""This route allows a user to view their account details and update them"""


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = AccountUpdate()
    if form.validate_on_submit():

        """Here is where it manages the photo file upload and commits it to the database, as well as the username and
            email"""
        if form.picture.data:
            picture_file = new_picture(form.picture.data)
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f"Account details for { form.username.data } changed !", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        """If no update is taking place it just displays the users information"""
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_photo = url_for("static", filename="profilephotos/" + current_user.image)
    return render_template(
        "account.html", title="Account", profile_photo=profile_photo, form=form
    )


"""This is the route for a creating a new review. When the user enters a review details and submits them they get
    added and committed to the database, the legend variabe at the end is to have a name on the HTML form."""


@app.route("/review/new", methods=["GET", "POST"])
@login_required
def new_review():
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            title=form.title.data,
            content=form.content.data,
            variety=form.variety.data,
            rating=form.rating.data,
            author=current_user,
        )
        db.session.add(review)
        db.session.commit()
        flash("Review Created!", "success")
        return redirect(url_for("home"))
    return render_template(
        "newreview.html", title="New Review", form=form, legend="New Review"
    )


"""This route queries the database for a specific review and shows the user. IF it cannot find the specified review
    it will return a 404 error"""


@app.route("/review/<int:review_id>")
def review(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template("review.html", title=review.title, review=review)


"""This route updates a review, the review will either sohow on the page or return a 404 if there is no review related
    to the given id. If the user inputs details for the review into the form it will commit it to the database and 
    redirect to the url of the review. """


@app.route("/review/<int:review_id>/update", methods=["GET", "POST"])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    form = ReviewForm()
    if form.validate_on_submit():
        review.title = form.title.data
        review.content = form.content.data
        review.variety = form.variety.data
        review.rating = form.rating.data
        db.session.commit()
        flash("Your Review has been updated!", "success")
        return redirect(url_for("review", review_id=review.id))
    elif request.method == "GET":
        form.title.data = review.title
        form.content.data = review.content
        form.variety.data = review.variety
        form.rating.data = review.rating
    return render_template(
        "newreview.html", title="Update Review", form=form, legend="Update Review"
    )


"""This route allows the user to delete a review, the delete will be made to the database and commited and the user will
    receive a message"""


@app.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash("Review Deleted :(!", "success")
    return redirect(url_for("home"))


"""This route will return the reviews by a user. It uses pagination like the homepage so if there are more than 5
    reviews on a page they will move onto another page"""


@app.route("/user/<string:username>", methods=["GET", "POST"])
def user_reviews(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    reviews = (
        Review.query.filter_by(author=user)
        .order_by(Review.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("userreviews.html", reviews=reviews, user=user)


"""This route cals the wineries.html file"""


@app.route("/wineries", methods=["GET"])
def wineries():
    return render_template("wineries.html")
