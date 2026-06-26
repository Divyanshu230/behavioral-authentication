import numpy as np


def extract_features(hold_time, flight_time, typing_speed):
    """
    Convert behavioral metrics into a feature vector
    for the machine learning model.
    """

    return np.array([
        [
            float(hold_time),
            float(flight_time),
            float(typing_speed)
        ]
    ])