from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
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
    year = db.Column(db.String, nullable=False)
    description = db.Column(db.String(250), nullable=True)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Integer, unique=False, nullable=True)
    review = db.Column(db.Text, unique=False, nullable=True)
    img_url = db.Column(db.Text, nullable=False)


class RateMovieForm(FlaskForm):
    rating = FloatField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


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


@app.route("/")
def home():
    db.session.query()
    all_films = Movie.query.order_by(Movie.rating.desc()).all()
    i = 0
    for item in all_films:
        item.ranking = len(all_films) - i
        i += 1
    return render_template("index.html", all_films=all_films)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)

    if request.method == "POST" and form.validate_on_submit():
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]
        db.session.commit()

        form.rating.default = movie_to_update.rating
        form.review.default = movie_to_update.review
        form.process()

        return redirect("/")

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

        return render_template("select.html", list_of_move=list_of_move)

    return render_template("add.html", form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect("/")


@app.route("/select", methods=["GET", "POST"])
def select():
    move_id = int(request.args.get('move_id'))
    for move in list_of_move:
        if move['id'] == move_id:
            new_move = Movie(title=move['title'],
                             year=move['release_date'],
                             description=move['overview'],
                             img_url=f"https://image.tmdb.org/t/p/w500/{move['poster_path']}")
            db.session.add(new_move)
            db.session.commit()
            move = Movie.query.filter_by(title=move['title'], year=move['release_date']).first()
            move_id = move.id

    return redirect(url_for('edit', id=move_id))


if __name__ == '__main__':
    app.run(debug=True)
