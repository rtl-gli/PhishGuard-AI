from urllib.parse import urlparse
import ipaddress


SUSPICIOUS_WORDS = [
    "login",
    "verify",
    "verification",
    "account",
    "secure",
    "update",
    "password",
    "bank",
    "signin",
    "confirm",
]


def has_ip_address(url):
    """Return 1 if the URL uses an IP address instead of a domain."""
    try:
        hostname = urlparse(url).hostname

        if hostname is None:
            return 0

        ipaddress.ip_address(hostname)
        return 1

    except ValueError:
        return 0


def extract_features(url):
    """Extract URL-based phishing indicators."""

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    features = {
        "url_length": len(url),

        "hostname_length": len(hostname),

        "number_of_dots": url.count("."),

        "number_of_hyphens": url.count("-"),

        "number_of_digits": sum(char.isdigit() for char in url),

        "number_of_special_characters": sum(
            not char.isalnum() for char in url
        ),

        "has_ip_address": has_ip_address(url),

        "has_at_symbol": int("@" in url),

        "has_https": int(parsed.scheme.lower() == "https"),

        "has_suspicious_word": int(
            any(word in url.lower() for word in SUSPICIOUS_WORDS)
        ),

        "number_of_subdomains": max(0, hostname.count(".") - 1),

        "path_length": len(parsed.path),

        "query_length": len(parsed.query),

        "has_double_slash": int("//" in parsed.path),

    }

    return features

if __name__ == "__main__":
    test_url = "https://secure-login-example.com/account/verify"

    features = extract_features(test_url)

    for name, value in features.items():
        print(f"{name}: {value}")