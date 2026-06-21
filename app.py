"""
app.py

Main application entry point for the "Behavioral Biometric Authentication
for Phishing and Account Takeover Prevention" Flask application.

Responsibilities of this module:
- Create and configure the Flask application instance.
- Ensure the instance folder and SQLite database exist before the app
  starts serving requests.
- Define the application's base route(s).

Compatible with Python 3.12.
"""
from datetime import datetime
import os
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from flask_bcrypt import Bcrypt

from config import BASE_DIR, Config

# ----------------------------------------------------------------------------
# PATH CONSTANTS
# ----------------------------------------------------------------------------
# Path to the SQL schema file used to initialize a fresh database. Kept as
# an absolute path (relative to this file) so the app behaves consistently
# regardless of the directory it is launched from.
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
bcrypt = Bcrypt()


# ----------------------------------------------------------------------------
# DATABASE INITIALIZATION
# ----------------------------------------------------------------------------
def init_db():
    """
    Initialize the SQLite database from the SQL schema file.

    Reads database/schema.sql and executes it against the SQLite database
    located at Config.DATABASE_PATH, creating all required tables. This is
    intended to be called only when the database file does not already
    exist, so that existing data is never overwritten.

    Uses Python's built-in sqlite3 module directly (no ORM), per project
    requirements.
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    # Connect directly to the SQLite file defined in the configuration and
    # execute the full schema script. `executescript` allows running the
    # multi-statement SQL file (CREATE TABLE, CREATE INDEX, etc.) in one go.
    connection = sqlite3.connect(Config.DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()


def ensure_database_exists():
    """
    Ensure the instance folder and SQLite database file exist.

    - Creates the instance/ folder if it is missing (Flask convention for
      environment-specific files such as local databases).
    - Creates instance/auth.db from database/schema.sql only if the
      database file does not already exist, preventing accidental data
      loss on every app restart.
    """
    # Ensure the instance/ directory exists before SQLite tries to create
    # a file inside it.
    os.makedirs(Config.INSTANCE_DIR, exist_ok=True)

    # Only initialize the database if it doesn't already exist, so that
    # restarting the app never wipes existing user data.
    if not os.path.isfile(Config.DATABASE_PATH):
        init_db()


# ----------------------------------------------------------------------------
# APPLICATION FACTORY
# ----------------------------------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(Config.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_app():
    """
    Application factory for creating and configuring the Flask app.
    """
    app = Flask(__name__)

    app.config.from_object(Config)
    bcrypt.init_app(app)

    Config.init_app(app)
    ensure_database_exists()

    @app.route("/")
    def index():
        return "Behavioral Biometric Authentication System Running"

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        hold_time = request.form.get("hold_time", 0)
        flight_time = request.form.get("flight_time", 0)
        typing_speed = request.form.get("typing_speed", 0)

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        connection = get_db_connection()

        try:
            existing_username = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if existing_username:
                flash("Username already exists.", "error")
                return redirect(url_for("register"))

            existing_email = connection.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if existing_email:
                flash("Email already exists.", "error")
                return redirect(url_for("register"))

            password_hash = bcrypt.generate_password_hash(
                password
            ).decode("utf-8")

            connection.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash)
            )

            user_id = connection.execute(
                "SELECT last_insert_rowid()"
            ).fetchone()[0]

            connection.execute(
                """
                INSERT INTO behavior_profiles
                (
                    user_id,
                    avg_hold_time,
                    avg_flight_time,
                    avg_typing_speed
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    hold_time,
                    flight_time,
                    typing_speed
                )
            )

            connection.commit()

        finally:
            connection.close()

        flash("Registration successful!", "success")
        return redirect(url_for("register"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("login"))

        hold_time = float(
            request.form.get("hold_time", 0)
        )

        flight_time = float(
            request.form.get("flight_time", 0)
        )

        typing_speed = float(
            request.form.get("typing_speed", 0)
        )
        print("Hold:", hold_time)
        print("Flight:", flight_time)
        print("Speed:", typing_speed)

        connection = get_db_connection()

        try:
            user = connection.execute(
                """
                SELECT id, username, email, password_hash
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if user is None or not bcrypt.check_password_hash(
            user["password_hash"],
            password
        ):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        connection = get_db_connection()

        try:
            profile = connection.execute(
                """
                SELECT
                    avg_hold_time,
                    avg_flight_time,
                    avg_typing_speed
                FROM behavior_profiles
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (user["id"],)
            ).fetchone()

        finally:
            connection.close()

        if profile:
            hold_diff = abs(
                float(profile["avg_hold_time"]) - hold_time
            )

            flight_diff = abs(
                float(profile["avg_flight_time"]) - flight_time
            )

            speed_diff = abs(
                float(profile["avg_typing_speed"]) - typing_speed
            )

            score = 100 - (
                hold_diff * 0.2 +
                flight_diff * 0.05 +
                speed_diff * 10
            )

            score = max(0, min(100, score))

        else:
            score = 50

        if score >= 80:
            risk = "LOW"
        elif score >= 60:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["behavior_score"] = round(score, 2)
        session["risk_level"] = risk
        session["hold_time"] = round(hold_time, 2)
        session["flight_time"] = round(flight_time, 2)
        session["typing_speed"] = round(typing_speed, 2)
        session["auth_status"] = "VERIFIED"
        session["login_timestamp"] = datetime.now().strftime(
         "%d-%b-%Y %H:%M:%S"
        )

        if score < 70:
            flash(
                f"Login blocked. Suspicious behavior detected. Score: {score:.2f}%",
                "error"
            )
            return redirect(url_for("login"))

        flash(
            f"Behavior Match Score: {score:.2f}%",
            "success"
        )

        flash(
            f"Welcome back, {user['username']}!",
            "success"
        )

        return redirect(url_for("dashboard"))

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out successfully.", "success")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        return render_template(
            "dashboard.html",
            username=session.get("username"),
            behavior_score=session.get("behavior_score"),
            risk_level=session.get("risk_level"),
            hold_time=session.get("hold_time"),
            flight_time=session.get("flight_time"),
            typing_speed=session.get("typing_speed"),
            auth_status=session.get("auth_status"),
            login_timestamp=session.get("login_timestamp")
        )

    return app


 
# ----------------------------------------------------------------------------
# APPLICATION ENTRY POINT
# ----------------------------------------------------------------------------
# Creating the app at module level allows it to be discovered by WSGI
# servers (e.g. `flask run`, gunicorn pointing at `app:app`) while still
# benefiting from the factory pattern above.
app = create_app()

if __name__ == "__main__":
    # app.config["DEBUG"] is sourced from Config, which reads the
    # FLASK_DEBUG environment variable (defaults to enabled for local dev).
    app.run(debug=app.config.get("DEBUG", False))