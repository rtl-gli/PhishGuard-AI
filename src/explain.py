import joblib
import pandas as pd

from src.features import extract_features


MODEL_PATH = "model/phishing_model.pkl"


FEATURE_NAMES = {
    "url_length": "URL length",
    "hyphen_count": "Hyphens",
    "digit_count": "Digits",
    "subdomain_count": "Subdomains",
    "trusted_tld": "Trusted TLD",
    "protocol_exists": "Protocol",
    "special_char_count": "Special characters",
    "entropy": "URL entropy",
    "path_depth": "Path depth",
    "domain_length": "Domain length",
    "is_domain_ip": "IP address domain",
    "has_at_symbol": "@ symbol",
    "has_double_slash_redirect": "Double-slash redirect",
    "tld_length": "TLD length",
    "query_param_count": "Query parameters",
    "path_length": "Path length",
}


def explain_url(url):
    model_data = joblib.load(MODEL_PATH)

    model = model_data["model"]
    feature_columns = model_data["features"]

    features = extract_features(url)

    data = pd.DataFrame(
        [[features[column] for column in feature_columns]],
        columns=feature_columns,
    )

    prediction = model.predict(data)[0]

    probabilities = model.predict_proba(data)[0]

    phishing_probability = probabilities[
        list(model.classes_).index(1)
    ]

    # Random Forest feature importance
    importances = model.feature_importances_

    ranked_features = sorted(
        zip(feature_columns, importances),
        key=lambda item: item[1],
        reverse=True,
    )

    explanations = []

    for feature, importance in ranked_features[:8]:
        value = features[feature]

        if value != 0:
            explanations.append(
                {
                    "feature": feature,
                    "name": FEATURE_NAMES.get(feature, feature),
                    "value": value,
                    "importance": float(importance),
                }
            )

    return {
        "url": url,
        "prediction": int(prediction),
        "phishing_probability": float(phishing_probability),
        "explanations": explanations,
    }