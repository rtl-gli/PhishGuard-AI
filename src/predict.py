import joblib
import pandas as pd


# Load trained model
model = joblib.load("model/phishing_model.pkl")


def predict_website(features):
    """
    Predict whether a website is legitimate or phishing.

    Parameters:
        features: Dictionary containing the website features.

    Returns:
        Prediction from the trained model.
    """

    data = pd.DataFrame([features])

    prediction = model.predict(data)[0]

    return prediction