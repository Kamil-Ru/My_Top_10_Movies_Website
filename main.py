from pprint import pprint

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired
from password import TMDB_API_KEY
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Movie_database.db"
Bootstrap(app)

db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=True)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, unique=True, nullable=True)
    img_url = db.Column(db.Text, nullable=False)


class RateMovieForm(FlaskForm):
    rating = FloatField(label='New rating: ', validators=[DataRequired()])
    review = StringField(label="New review: ", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


class AddMovieForm(FlaskForm):
    title = StringField(label="Title: ", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


if not os.path.isfile("books-collection.db"):
    db.create_all()

TMDB_Endpoint = "https://api.themoviedb.org/3/search/movie"

parameters = {
    "api_key": TMDB_API_KEY,
    "language": "en-US",
    "query": "move"
}

"""
new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)

db.session.add(new_movie)
db.session.commit()
"""


@app.route("/")
def home():
    all_films = Movie.query.all()
    return render_template("index.html", all_films=all_films)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)

    form = RateMovieForm()

    if request.method == "POST" and form.validate_on_submit():
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]
        db.session.commit()
        return redirect("/")

    form.rating.default = movie_to_update.rating
    form.review.default = movie_to_update.review
    form.process()

    return render_template("edit.html", form=form)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()

    if request.method == "POST" and form.validate_on_submit():
        parameters["query"] = form.title.data
        response = requests.get(TMDB_Endpoint, params=parameters)
        response.raise_for_status()
        data = response.json()
        global list_of_move
        list_of_move = []
        for move in data['results']:
            list_of_move.append(move)
            #print(move)

        return render_template("select.html", list_of_move=list_of_move)

    return render_template("add.html", form=form)


@app.route("/select", methods=["GET", "POST"])
def select():
    print("OK")
    move_id = int(request.args.get('move_id'))

    for move in list_of_move:
        if move['id'] == move_id:
            new_move = Movie(id=move['id'], title=move['title'], year=move['release_date'], description=move['overview'], ranking=move['vote_average'], img_url=f"https://image.tmdb.org/t/p/w500/{move['poster_path']}")
            db.session.add(new_move)
            db.session.commit()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
