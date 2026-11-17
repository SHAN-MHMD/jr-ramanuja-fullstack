import os
import sqlite3
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
# Set SECRET_KEY in your environment before deploying publicly.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create an empty local database on first run."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                operation TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL
            )
        """)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["username"] = user["username"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="❌ Invalid Username or Password")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_text = request.form.get("age", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, age_text, username, password, confirm_password]):
            return render_template("register.html", error="Please fill in all fields.")

        if not age_text.isdigit() or not 1 <= int(age_text) <= 120:
            return render_template("register.html", error="Please enter a valid age.")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters.")

        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO users (name, age, username, password) VALUES (?, ?, ?, ?)",
                    (name, int(age_text), username, generate_password_hash(password))
                )
        except sqlite3.IntegrityError:
            return render_template("register.html", error="❌ Username already exists!")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    with get_db_connection() as conn:
        data = conn.execute("""
            SELECT COALESCE(SUM(total_questions), 0) AS questions_solved,
                   COALESCE(AVG(score * 100.0 / NULLIF(total_questions, 0)), 0) AS accuracy
            FROM quiz_results
            WHERE username = ?
        """, (username,)).fetchone()

    return render_template(
        "dashboard.html",
        name=session.get("name", "Student"),
        questions_solved=data["questions_solved"],
        accuracy=round(data["accuracy"]),
        daily_streak=0
    )


@app.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@app.route("/progress")
@login_required
def progress():
    username = session["username"]
    with get_db_connection() as conn:
        data = conn.execute("""
            SELECT COUNT(*) AS quizzes_taken,
                   COALESCE(SUM(total_questions), 0) AS questions_solved,
                   COALESCE(MAX(score), 0) AS best_score,
                   COALESCE(AVG(score * 100.0 / NULLIF(total_questions, 0)), 0) AS accuracy
            FROM quiz_results
            WHERE username = ?
        """, (username,)).fetchone()

    return render_template(
        "progress.html",
        quizzes_taken=data["quizzes_taken"],
        questions_solved=data["questions_solved"],
        best_score=data["best_score"],
        accuracy=round(data["accuracy"])
    )


@app.route("/save_result", methods=["POST"])
@login_required
def save_result():
    operation = request.form.get("operation", "")
    try:
        score = int(request.form.get("score", ""))
        total_questions = int(request.form.get("total_questions", ""))
    except ValueError:
        return "Invalid quiz result", 400

    allowed_operations = {"addition", "subtraction", "multiplication", "division", "random"}
    if operation not in allowed_operations:
        return "Invalid operation", 400
    if total_questions < 1 or not 0 <= score <= total_questions:
        return "Invalid score", 400

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO quiz_results (username, operation, score, total_questions)
            VALUES (?, ?, ?, ?)
        """, (session["username"], operation, score, total_questions))

    return "saved", 200


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
