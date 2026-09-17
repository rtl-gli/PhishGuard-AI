import joblib
import pandas as pd

from features import extract_features


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
    """Explain a Decision Tree prediction using its decision path."""

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

    # Find the decision path taken by this URL.
    node_indicator = model.decision_path(data)

    leaf_id = model.apply(data)[0]

    node_ids = node_indicator.indices[
        node_indicator.indptr[0]:
        node_indicator.indptr[1]
    ]

    decisions = []

    for node_id in node_ids:

        if node_id == leaf_id:
            continue

        feature_index = model.tree_.feature[node_id]
        threshold = model.tree_.threshold[node_id]

        feature = feature_columns[feature_index]
        value = features[feature]

        if value <= threshold:
            direction = "<="
        else:
            direction = ">"

        decisions.append(
            {
                "feature": feature,
                "value": value,
                "threshold": threshold,
                "direction": direction,
            }
        )

    return {
        "url": url,
        "prediction": int(prediction),
        "phishing_probability": float(phishing_probability),
        "decisions": decisions,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src\\explain.py <URL>")
        raise SystemExit(1)

    url = sys.argv[1]

    result = explain_url(url)

    print(f"URL: {result['url']}")
    print(
        f"Phishing probability: "
        f"{result['phishing_probability']:.2%}"
    )

    if result["prediction"] == 1:
        print("Prediction: Potentially phishing")
    else:
        print("Prediction: Likely legitimate")

    print("\nDecision path:")

    for number, decision in enumerate(
        result["decisions"],
        start=1,
    ):

        name = FEATURE_NAMES.get(
            decision["feature"],
            decision["feature"],
        )

        print(
            f"{number}. {name} "
            f"{decision['direction']} "
            f"{decision['threshold']:.3f} "
            f"(value: {decision['value']})"
        )