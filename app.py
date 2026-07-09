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
from multiprocessing import connection
from multiprocessing import connection
from tkinter.tix import MAX

from ml.evaluate_model import (
    predict_behavior,
    calculate_similarity_score,
    calculate_ml_confidence,
    calculate_behavior_score,
    calculate_risk_level
)
from datetime import datetime
from zoneinfo import ZoneInfo
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
from flask import request, jsonify
import random

# ==========================================
# Authentication Configuration
# ==========================================

MIN_BEHAVIOR_SCORE = 60



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
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")
        
        hold_time = float(request.form.get("hold_time", 0))
        flight_time = float(request.form.get("flight_time", 0))
        typing_speed = float(request.form.get("typing_speed", 0))
        
        if flight_time > 600:
            flash(
                "Typing sample is inconsistent. Please type naturally and try again.",
                "error"
            )
            return redirect(url_for("register"))

        if typing_speed < 2:
            flash(
                "Typing speed is too slow. Please register again.",
                "error"
            )
            return redirect(url_for("register"))

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

        # =====================================================
        # Calculate Similarity Score
        # =====================================================

        if profile:
            similarity_score = calculate_similarity_score(
                hold_time,
                flight_time,
                typing_speed,
                float(profile["avg_hold_time"]),
                float(profile["avg_flight_time"]),
                float(profile["avg_typing_speed"])
            )
        else:
            similarity_score = 50

        # =====================================================
        # Isolation Forest Prediction
        # =====================================================

        ml_prediction, decision_score = predict_behavior(
            hold_time,
            flight_time,
            typing_speed
        )

        ml_confidence = calculate_ml_confidence(
            ml_prediction,
            decision_score
        )

        # =====================================================
        # Final Behavior Score
        # =====================================================

        behavior_score = calculate_behavior_score(
            similarity_score,
            ml_confidence
        )

        # =====================================================
        # Risk Level
        # =====================================================

        risk = calculate_risk_level(
            behavior_score
        )
        print("\n========== LOGIN ANALYSIS ==========")
        print("Similarity Score :", similarity_score)
        print("ML Prediction    :", ml_prediction)
        print("Decision Score   :", decision_score)
        print("ML Confidence    :", ml_confidence)
        print("Behavior Score   :", behavior_score)
        print("Risk Level       :", risk)
        print("===================================\n")


        # ----------------------------------------
        # Block suspicious logins
        # ----------------------------------------
        if behavior_score < MIN_BEHAVIOR_SCORE:
            flash(
                f"Login blocked. Behavior score ({behavior_score:.2f}%) is below the minimum required score ({MIN_BEHAVIOR_SCORE}%).",
                "error"
            )
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["behavior_score"] = behavior_score
        session["similarity_score"] = similarity_score
        session["ml_confidence"] = ml_confidence
       

        session["ml_prediction"] = (
            "Normal"
            if ml_prediction == 1
            else "Anomaly"
        )
        session["risk_level"] = risk
        session["hold_time"] = round(hold_time, 2)
        session["flight_time"] = round(flight_time, 2)
        session["typing_speed"] = round(typing_speed, 2)
        session["auth_status"] = "VERIFIED"
        session["login_timestamp"] = datetime.now().strftime(
            "%d-%b-%Y %H:%M:%S"
        )
        connection = get_db_connection()

        # ==========================================
        # Adaptive Profile Update
        # ==========================================

        new_hold = (
            float(profile["avg_hold_time"]) * 0.8 +
            hold_time * 0.2
        )

        new_flight = (
            float(profile["avg_flight_time"]) * 0.8 +
            flight_time * 0.2
        )

        new_speed = (
            float(profile["avg_typing_speed"]) * 0.8 +
            typing_speed * 0.2
        )

        connection.execute(
            """
            UPDATE behavior_profiles
            SET
                avg_hold_time = ?,
                avg_flight_time = ?,
                avg_typing_speed = ?
            WHERE user_id = ?
            """,
            (
                round(new_hold, 2),
                round(new_flight, 2),
                round(new_speed, 2),
                user["id"]
            )
        )

        print("\n===== PROFILE UPDATED =====")
        print("Old Hold :", profile["avg_hold_time"])
        print("New Hold :", round(new_hold, 2))
        print("Old Flight :", profile["avg_flight_time"])
        print("New Flight :", round(new_flight, 2))
        print("Old Speed :", profile["avg_typing_speed"])
        print("New Speed :", round(new_speed, 2))
        print("===========================\n")

        try:
            login_time = datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).strftime("%Y-%m-%d %H:%M:%S")
            connection.execute(
                """
                INSERT INTO login_history
                (
                    user_id,
                    login_time,
                    behavior_score,
                    risk_level,
                    status,
                    ip_address
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user["id"],
                    login_time,
                    behavior_score,
                    risk,
                    "SUCCESS",
                    request.remote_addr
                )
            )

            connection.commit()

        finally:
            connection.close()

        

        flash(
            f"Behavior Match Score: {behavior_score:.2f}%",
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
            return redirect(url_for("login"))

        connection = get_db_connection()

        try:

            login_history = connection.execute(
                """
                SELECT
                    login_time,
                    behavior_score,
                    risk_level,
                    status
                FROM login_history
                WHERE user_id = ?
                ORDER BY login_time DESC
                LIMIT 10
                """,
                (session["user_id"],)
            ).fetchall()
            risk_counts = connection.execute(
                """
                SELECT
                    risk_level,
                    COUNT(*) as total
                FROM login_history
                WHERE user_id = ?
                GROUP BY risk_level
                """,
                (session["user_id"],)
            ).fetchall()

            risk_labels = []
            risk_values = []

            for row in risk_counts:
                risk_labels.append(row["risk_level"])
                risk_values.append(row["total"])

            total_logins, average_score, highest_score, lowest_score = connection.execute(
                """
            SELECT
            COUNT(*) AS total,
            AVG(behavior_score),
            MAX(behavior_score),
            MIN(behavior_score)
            FROM login_history
            WHERE user_id = ?
            """,
            (session["user_id"],)
            ).fetchone()
            average_score = round(average_score, 2) if average_score else 0
            highest_score = highest_score or 0
            lowest_score = lowest_score or 0
            

        finally:
            connection.close()

        chart_labels = [
            datetime.strptime(
                entry["login_time"],
                "%Y-%m-%d %H:%M:%S",
            ).strftime("%H:%M")
            for entry in reversed(login_history)
        ]
        chart_scores = [entry["behavior_score"] for entry in reversed(login_history)]

        return render_template(
            "dashboard.html",
            username=session.get("username"),
            behavior_score=session.get("behavior_score"),
            ml_prediction=session["ml_prediction"],
            risk_level=session.get("risk_level"),
            hold_time=session.get("hold_time"),
            flight_time=session.get("flight_time"),
            typing_speed=session.get("typing_speed"),
            auth_status=session.get("auth_status"),
            login_timestamp=session.get("login_timestamp"),
            login_history=login_history,
            total_logins=total_logins,
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            chart_labels=chart_labels,
            chart_scores=chart_scores,
            risk_labels=risk_labels,
            risk_values=risk_values
        )

    @app.route("/continuous_check", methods=["POST"])
    def continuous_check():

        data = request.get_json()

        hold_time = float(data.get("hold_time", 0))
        flight_time = float(data.get("flight_time", 0))
        typing_speed = float(data.get("typing_speed", 0))

        connection = get_db_connection()

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
            (session["user_id"],)
        ).fetchone()

        connection.close()

        similarity_score = calculate_similarity_score(
            hold_time,
            flight_time,
            typing_speed,
            float(profile["avg_hold_time"]),
            float(profile["avg_flight_time"]),
            float(profile["avg_typing_speed"])
        )
        if not profile:
            return jsonify({
                "error": "Behavior profile not found"
            }), 400

        ml_prediction , decision_score = predict_behavior(
            hold_time,
            flight_time,
            typing_speed
        )
        ml_confidence = calculate_ml_confidence(
            ml_prediction,
            decision_score
        )
        behavior_score = calculate_behavior_score(
            similarity_score,
            ml_confidence
        )
        risk = calculate_risk_level(
            behavior_score
        )

        prediction_text = (
            "Normal" if ml_prediction == 1 else "Anomaly"
        )
        print("\n====== CONTINUOUS CHECK ======")
        print("Hold:", hold_time)
        print("Flight:", flight_time)
        print("Speed:", typing_speed)
        print("Similarity:", similarity_score)
        print("ML Prediction:", ml_prediction)
        print("Decision Score:", decision_score)
        print("ML Confidence:", ml_confidence)
        print("Behavior Score:", behavior_score)
        print("Risk:", risk)
        print("==============================\n")
        

        return jsonify({
            "behavior_score": behavior_score,
            "prediction": prediction_text,
            "risk_level": risk,
            "hold_time": round(hold_time, 2),
            "flight_time": round(flight_time, 2),
            "typing_speed": round(typing_speed, 2),
            "similarity_score": round(similarity_score, 2),
            "ml_confidence": round(ml_confidence, 2)
        })

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