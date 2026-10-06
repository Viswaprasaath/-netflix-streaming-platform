import os
from dotenv import load_dotenv

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

load_dotenv()

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

@app.route("/")
def home():
    return "Netflix Backend is Running!"


# GET all movies
@app.route("/movies", methods=["GET"])
def movies():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM movies")

    result = cursor.fetchall()

    cursor.close()

    return jsonify(result)


# GET one movie
@app.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM movies WHERE id = %s",
        (movie_id,)
    )

    movie = cursor.fetchone()

    cursor.close()

    if movie is None:
        return jsonify({"message": "Movie not found"}), 404

    return jsonify(movie)


# POST a new movie
@app.route("/movies", methods=["POST"])
def add_movie():
    data = request.get_json()

    cursor = db.cursor()

    query = """
        INSERT INTO movies
        (title, description, genre, release_year, rating)
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        data["title"],
        data["description"],
        data["genre"],
        data["release_year"],
        data["rating"]
    )

    cursor.execute(query, values)

    db.commit()

    movie_id = cursor.lastrowid

    cursor.close()

    return jsonify({
        "message": "Movie added successfully",
        "movie_id": movie_id
    }), 201
# UPDATE a movie
@app.route("/movies/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    data = request.get_json()

    cursor = db.cursor()

    query = """
        UPDATE movies
        SET title = %s,
            description = %s,
            genre = %s,
            release_year = %s,
            rating = %s
        WHERE id = %s
    """

    values = (
        data["title"],
        data["description"],
        data["genre"],
        data["release_year"],
        data["rating"],
        movie_id
    )

    cursor.execute(query, values)
    db.commit()

    if cursor.rowcount == 0:
        cursor.close()
        return jsonify({"message": "Movie not found"}), 404

    cursor.close()

    return jsonify({
        "message": "Movie updated successfully",
        "movie_id": movie_id
    })
# DELETE a movie
@app.route("/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM movies WHERE id = %s",
        (movie_id,)
    )

    db.commit()

    if cursor.rowcount == 0:
        cursor.close()
        return jsonify({"message": "Movie not found"}), 404

    cursor.close()

    return jsonify({
        "message": "Movie deleted successfully",
        "movie_id": movie_id
    })
# USER REGISTRATION
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data["name"]
    email = data["email"]
    password = data["password"]

    cursor = db.cursor()

    query = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
    """

    values = (name, email, password)

    cursor.execute(query, values)

    db.commit()

    user_id = cursor.lastrowid

    cursor.close()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user_id
    }), 201
# USER LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT id, name, email, password
        FROM users
        WHERE email = %s
    """

    cursor.execute(query, (email,))

    user = cursor.fetchone()

    cursor.close()

    if user is None:
        return jsonify({"message": "Invalid email or password"}), 401

    if user["password"] != password:
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"]
    })
# ADD WATCH HISTORY
@app.route("/watch-history", methods=["POST"])
def add_watch_history():
    data = request.get_json()

    user_id = data["user_id"]
    movie_id = data["movie_id"]

    cursor = db.cursor()

    query = """
        INSERT INTO watch_history (user_id, movie_id)
        VALUES (%s, %s)
    """

    cursor.execute(query, (user_id, movie_id))

    db.commit()

    history_id = cursor.lastrowid

    cursor.close()

    return jsonify({
        "message": "Watch history added",
        "history_id": history_id
    }), 201
# GET USER WATCH HISTORY
@app.route("/watch-history/<int:user_id>", methods=["GET"])
def get_watch_history(user_id):
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            movies.id,
            movies.title,
            movies.genre,
            movies.release_year,
            movies.rating,
            watch_history.watched_at
        FROM watch_history
        JOIN movies
            ON watch_history.movie_id = movies.id
        WHERE watch_history.user_id = %s
        ORDER BY watch_history.watched_at DESC
    """

    cursor.execute(query, (user_id,))

    history = cursor.fetchall()

    cursor.close()

    return jsonify(history)
# ADD FAVORITE
@app.route("/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json()

    user_id = data["user_id"]
    movie_id = data["movie_id"]

    cursor = db.cursor()

    query = """
        INSERT INTO favorites (user_id, movie_id)
        VALUES (%s, %s)
    """

    cursor.execute(query, (user_id, movie_id))

    db.commit()

    favorite_id = cursor.lastrowid

    cursor.close()

    return jsonify({
        "message": "Movie added to favorites",
        "favorite_id": favorite_id
    }), 201
# GET FAVORITES
@app.route("/favorites/<int:user_id>", methods=["GET"])
def get_favorites(user_id):
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            movies.id,
            movies.title,
            movies.description,
            movies.genre,
            movies.release_year,
            movies.rating
        FROM favorites
        JOIN movies
            ON favorites.movie_id = movies.id
        WHERE favorites.user_id = %s
    """

    cursor.execute(query, (user_id,))

    favorites = cursor.fetchall()

    cursor.close()

    return jsonify(favorites)
# DELETE FAVORITE
@app.route("/favorites/<int:user_id>/<int:movie_id>", methods=["DELETE"])
def delete_favorite(user_id, movie_id):
    cursor = db.cursor()

    query = """
        DELETE FROM favorites
        WHERE user_id = %s AND movie_id = %s
    """

    cursor.execute(query, (user_id, movie_id))

    db.commit()

    if cursor.rowcount == 0:
        cursor.close()
        return jsonify({"message": "Favorite not found"}), 404

    cursor.close()

    return jsonify({
        "message": "Movie removed from favorites"
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
