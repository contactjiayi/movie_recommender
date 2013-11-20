from flask import Flask, render_template, redirect, request, session, url_for, flash
import model
from model import session as model_session
import datetime

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

@app.route("/")
def index():
    email = session.get("email")
    if email:
         return "User %s is logged in!" % email
    else:
        return render_template("index.html")

@app.route("/", methods=["POST"])
def process_login():
    email = request.form.get("email")
    password = request.form.get("password")

    user_id = authenticate(email, password)
    if user_id:
        flash("User authenticated!")
        session['user_id'] = user_id
        users = view_users()
        return render_template("user_list.html", users=users)
    else:
        flash("Password incorrect, there may be a ferret stampede in progress")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    flash('Logged out!')
    return redirect(url_for("index"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def create_account():
    email = request.form.get("email")
    password = request.form.get("password")
    make_new_user(email, password)

    return redirect(url_for("index"))

@app.route("/user/<user_id>")
def user_ratings(user_id):
    user = model_session.query(model.User).filter_by(id=user_id).one()
    return render_template("movies_ratings.html", user=user, user_id=user_id)


@app.route("/view_movie/<movie_id>")
def movie_ratings(movie_id):
    user_id = session['user_id']
    user = model_session.query(model.User).filter_by(id=user_id).one()
    movie = model_session.query(model.Movie).filter_by(id=movie_id).one()
    user_rating = model_session.query(model.Rating).filter_by(movie_id=movie.id, user_id=user.id).all()

    sum_ratings = 0
    all_ratings = movie.ratings
    for rating in all_ratings:
        sum_ratings += rating.rating
    avg_rating = sum_ratings / len(all_ratings)
    
    rating = None
    prediction = None
    if len(user_rating) >= 1:
        rating = user_rating[0]
        effective_rating = rating.rating
    else:
        prediction = user.predict_rating(movie)
        effective_rating = prediction

    the_eye = model_session.query(model.User).filter_by(email="theeye@ofjudgement.com").one()
    eye_rating = model_session.query(model.Rating).filter_by(user_id=the_eye.id, movie_id=movie_id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(movie)
    else:
        eye_rating = eye_rating.rating

    difference = abs(eye_rating - effective_rating)

    messages = [ "I suppose you don't have such bad taste after all.",
             "I regret every decision that I've ever made that has brought me to listen to your opinion.",
             "Words fail me, as your taste in movies has clearly failed you.",
             "That movie is great. For a clown to watch. Idiot.", 
             "This movie is horrible.", 
             "This movie is good. Just for you"]

    beratement = messages[int(difference)]

    return render_template("view_movie.html", user=user, movie=movie, movie_id=movie_id, rating=rating, prediction=prediction, avg_rating=avg_rating, beratement=beratement)

@app.route("/view_movie/<movie_id>", methods=["POST"])
def update_rating(movie_id):
    user_id = session['user_id']
    user_rating = model_session.query(model.Rating).filter_by(movie_id=movie_id, user_id=user_id).all()
    updated_rating = request.form.get("rating")

    if len(user_rating) == 0:
        add_rating(user_id, movie_id, updated_rating, datetime.datetime.now())
    else:
        change_rating(user_id, movie_id, updated_rating, datetime.datetime.now())

    return redirect(url_for("movie_ratings", movie_id=movie_id))


def authenticate(email, password):
    try:
        user = model_session.query(model.User).filter_by(email=email).one()
        if user.password == password:
            return user.id
    except:
        return "Email doesn't exist"

def make_new_user(email, password):
    new_user = model.User(email=email, password=password)
    model_session.add(new_user)
    model_session.commit()

def view_users():
    users = model_session.query(model.User).limit(5).all()
    return users

def add_rating(user_id, movie_id, rating, timestamp):
    new_rating = model.Rating(user_id=user_id, movie_id=movie_id, rating=rating, timestamp=timestamp)
    model_session.add(new_rating)
    model_session.commit()

def change_rating(user_id, movie_id, updated_rating, timestamp):
    original_rating = model_session.query(model.Rating).filter_by(user_id=user_id, movie_id=movie_id).one()
    original_rating.rating = updated_rating
    model_session.commit()

if __name__ == "__main__":
    app.run(debug=True)