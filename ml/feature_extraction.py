import pandas as pd


def extract_features(
    hold_time,
    flight_time,
    typing_speed
):
    """
    Convert behavioral metrics into a DataFrame
    matching the training features.
    """

    return pd.DataFrame(
        [
            [
                float(hold_time),
                float(flight_time),
                float(typing_speed)
            ]
        ],
        columns=[
            "avg_hold_time",
            "avg_flight_time",
            "avg_typing_speed"
        ]
    )