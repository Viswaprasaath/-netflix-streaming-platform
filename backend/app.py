
import os
from dotenv import load_dotenv

from flask import Flask, jsonify, request, g
from flask_cors import CORS
import mysql.connector

load_dotenv()

app = Flask(__name__)
CORS(app)


# DATABASE CONNECTION — ONE CONNECTION PER REQUEST
def get_db_connection():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            connection_timeout=10
        )
    return g.db


def get_cursor(dictionary=False):
    return get_db_connection().cursor(dictionary=dictionary)


@app.teardown_appcontext
def close_db_connection(exception=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


# HOME
@app.route("/")
def home():
    return "Netflix Backend is Running!"


# GET ALL MOVIES
@app.route("/movies", methods=["GET"])
def movies():
    cursor = get_cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM movies")
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()


# GET ONE MOVIE
@app.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    cursor = get_cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM movies WHERE id = %s",
            (movie_id,)
        )
        movie = cursor.fetchone()

        if movie is None:
            return jsonify({"message": "Movie not found"}), 404

        return jsonify(movie)
    finally:
        cursor.close()


# ADD MOVIE
@app.route("/movies", methods=["POST"])
def add_movie():
    data = request.get_json(silent=True) or {}
    required = ["title", "description", "genre", "release_year", "rating"]

    if any(key not in data for key in required):
        return jsonify({"message": "Missing required movie fields"}), 400

    cursor = get_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO movies
            (title, description, genre, release_year, rating)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["title"],
                data["description"],
                data["genre"],
                data["release_year"],
                data["rating"]
            )
        )
        get_db_connection().commit()
        movie_id = cursor.lastrowid

        return jsonify({
            "message": "Movie added successfully",
            "movie_id": movie_id
        }), 201
    finally:
        cursor.close()


# UPDATE MOVIE
@app.route("/movies/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    data = request.get_json(silent=True) or {}
    required = ["title", "description", "genre", "release_year", "rating"]

    if any(key not in data for key in required):
        return jsonify({"message": "Missing required movie fields"}), 400

    cursor = get_cursor()
    try:
        cursor.execute(
            """
            UPDATE movies
            SET title = %s, description = %s, genre = %s,
                release_year = %s, rating = %s
            WHERE id = %s
            """,
            (
                data["title"],
                data["description"],
                data["genre"],
                data["release_year"],
                data["rating"],
                movie_id
            )
        )
        get_db_connection().commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Movie not found"}), 404

        return jsonify({
            "message": "Movie updated successfully",
            "movie_id": movie_id
        })
    finally:
        cursor.close()


# DELETE MOVIE
@app.route("/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    cursor = get_cursor()
    try:
        cursor.execute(
            "DELETE FROM movies WHERE id = %s",
            (movie_id,)
        )
        get_db_connection().commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Movie not found"}), 404

        return jsonify({
            "message": "Movie deleted successfully",
            "movie_id": movie_id
        })
    finally:
        cursor.close()


# USER REGISTRATION
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    required = ["name", "email", "password"]

    if any(not data.get(key) for key in required):
        return jsonify({"message": "Name, email and password are required"}), 400

    cursor = get_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (data["name"], data["email"], data["password"])
        )
        get_db_connection().commit()
        user_id = cursor.lastrowid

        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201
    finally:
        cursor.close()


# USER LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    cursor = get_cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )
        user = cursor.fetchone()

        if user is None or user["password"] != password:
            return jsonify({"message": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"]
        })
    finally:
        cursor.close()


# ADD WATCH HISTORY
@app.route("/watch-history", methods=["POST"])
def add_watch_history():
    data = request.get_json(silent=True) or {}

    if "user_id" not in data or "movie_id" not in data:
        return jsonify({"message": "user_id and movie_id are required"}), 400

    cursor = get_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO watch_history (user_id, movie_id)
            VALUES (%s, %s)
            """,
            (data["user_id"], data["movie_id"])
        )
        get_db_connection().commit()
        history_id = cursor.lastrowid

        return jsonify({
            "message": "Watch history added",
            "history_id": history_id
        }), 201
    finally:
        cursor.close()


# GET USER WATCH HISTORY
@app.route("/watch-history/<int:user_id>", methods=["GET"])
def get_watch_history(user_id):
    cursor = get_cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                movies.id,
                movies.title,
                movies.genre,
                movies.release_year,
                movies.rating,
                watch_history.watched_at
            FROM watch_history
            JOIN movies ON watch_history.movie_id = movies.id
            WHERE watch_history.user_id = %s
            ORDER BY watch_history.watched_at DESC
            """,
            (user_id,)
        )
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()


# ADD FAVORITE
@app.route("/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json(silent=True) or {}

    if "user_id" not in data or "movie_id" not in data:
        return jsonify({"message": "user_id and movie_id are required"}), 400

    cursor = get_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO favorites (user_id, movie_id)
            VALUES (%s, %s)
            """,
            (data["user_id"], data["movie_id"])
        )
        get_db_connection().commit()
        favorite_id = cursor.lastrowid

        return jsonify({
            "message": "Movie added to favorites",
            "favorite_id": favorite_id
        }), 201
    finally:
        cursor.close()


# GET FAVORITES
@app.route("/favorites/<int:user_id>", methods=["GET"])
def get_favorites(user_id):
    cursor = get_cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                movies.id,
                movies.title,
                movies.description,
                movies.genre,
                movies.release_year,
                movies.rating
            FROM favorites
            JOIN movies ON favorites.movie_id = movies.id
            WHERE favorites.user_id = %s
            """,
            (user_id,)
        )
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()


# DELETE FAVORITE
@app.route("/favorites/<int:user_id>/<int:movie_id>", methods=["DELETE"])
def delete_favorite(user_id, movie_id):
    cursor = get_cursor()
    try:
        cursor.execute(
            """
            DELETE FROM favorites
            WHERE user_id = %s AND movie_id = %s
            """,
            (user_id, movie_id)
        )
        get_db_connection().commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Favorite not found"}), 404

        return jsonify({"message": "Movie removed from favorites"})
    finally:
        cursor.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
