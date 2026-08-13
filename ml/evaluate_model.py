"""
Behavior Analysis Module

This module performs:

1. Similarity score calculation
2. Machine learning prediction
3. ML confidence estimation
4. Final behavior score calculation
5. Risk level classification

Author: Divyanshu Anand
"""
import joblib

from ml.feature_extraction import extract_features


# =====================================================
# Load trained Isolation Forest model
# =====================================================

saved_model = joblib.load("ml/behavior_model.pkl")

model = saved_model["model"]

SCORE_MIN = saved_model["score_min"]

SCORE_MAX = saved_model["score_max"]


# =====================================================
# Predict Behavior
# =====================================================

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

    prediction = model.predict(features)[0]

    decision_score = model.decision_function(features)[0]

    return prediction, decision_score


# =====================================================
# Similarity Score
# =====================================================

def calculate_similarity_score(
    current_hold,
    current_flight,
    current_speed,
    profile_hold,
    profile_flight,
    profile_speed
):

    hold_similarity = max(
        0,
        100 - (
            abs(current_hold - profile_hold)
            / max(profile_hold, 1)
        ) * 200
    )

    flight_similarity = max(
        0,
        100 - (
            abs(current_flight - profile_flight)
            / max(profile_flight, 1)
        ) * 200
    )

    speed_similarity = max(
        0,
        100 - (
            abs(current_speed - profile_speed)
            / max(profile_speed, 1)
        ) * 50
    )

    similarity = (

        hold_similarity * 0.45 +

        flight_similarity * 0.45 +

        speed_similarity * 0.10
    )
    print("Hold Similarity:", round(hold_similarity, 2))
    print("Flight Similarity:", round(flight_similarity, 2))
    print("Speed Similarity:", round(speed_similarity, 2))
    print("Similarity Score:", round(similarity, 2))

    return round(similarity, 2)


# =====================================================
# ML Confidence
# =====================================================

def calculate_ml_confidence(
    prediction,
    decision_score
):

    normalized = (
        decision_score - SCORE_MIN
    ) / (
        SCORE_MAX - SCORE_MIN
    )

    normalized = max(
        0,
        min(
            1,
            normalized
        )
    )

    if prediction == 1:

        confidence = 70 + normalized * 30

    else:

        confidence = normalized * 40

    return round(confidence, 2)


# =====================================================
# Final Behavior Score
# =====================================================

def calculate_behavior_score(
    similarity_score,
    ml_confidence
):

    score = (
        similarity_score * 0.95 +
        ml_confidence * 0.05
    )

    return round(score, 2)


# =====================================================
# Risk Level
# =====================================================

def calculate_risk_level(
    behavior_score
):

    if behavior_score >= 75:
        return "LOW"

    elif behavior_score >= 60:
        return "MEDIUM"

    return "HIGH"
# ----------------------------------------
# Complete Behavior Analysis
# ----------------------------------------

def analyze_behavior(
    hold_time,
    flight_time,
    typing_speed,
    profile_hold,
    profile_flight,
    profile_speed
):

    similarity_score = calculate_similarity_score(
        hold_time,
        flight_time,
        typing_speed,
        profile_hold,
        profile_flight,
        profile_speed
    )

    ml_prediction, decision_score = predict_behavior(
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

    return {
        "similarity_score": similarity_score,
        "ml_prediction": ml_prediction,
        "decision_score": decision_score,
        "ml_confidence": ml_confidence,
        "behavior_score": behavior_score,
        "risk": risk
    }