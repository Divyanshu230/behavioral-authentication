import joblib

from feature_extraction import extract_features


# ----------------------------------------
# Load trained model
# ----------------------------------------

model = joblib.load("ml/behavior_model.pkl")


# ----------------------------------------
# Predict user behavior
# ----------------------------------------

def predict_behavior(
    hold_time,
    flight_time,
    typing_speed
):

    features = extract_features(
        hold_time,
        flight_time,
        typing_speed
    )

    prediction = model.predict(features)

    return prediction[0]