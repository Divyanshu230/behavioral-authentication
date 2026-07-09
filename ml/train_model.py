import sqlite3
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest


# ------------------------------------
# Connect to SQLite Database
# ------------------------------------

connection = sqlite3.connect("instance/auth.db")


# ------------------------------------
# Read behavioral data
# ------------------------------------

query = """
SELECT
    avg_hold_time,
    avg_flight_time,
    avg_typing_speed
FROM behavior_profiles
"""

df = pd.read_sql_query(query, connection)

connection.close()


# ------------------------------------
# Prepare training data
# ------------------------------------

X = df[
    [
        "avg_hold_time",
        "avg_flight_time",
        "avg_typing_speed"
    ]
]


# ------------------------------------
# Train Isolation Forest
# ------------------------------------

model = IsolationForest(

    n_estimators=100,

    contamination=0.10,

    random_state=42

)

model.fit(X)

# ------------------------------------
# Calculate decision score range
# ------------------------------------

decision_scores = model.decision_function(X)

score_min = decision_scores.min()
score_max = decision_scores.max()



# ------------------------------------
# Save trained model
# ------------------------------------

joblib.dump(
    {
        "model": model,
        "score_min": score_min,
        "score_max": score_max
    },
    "ml/behavior_model.pkl"
)


