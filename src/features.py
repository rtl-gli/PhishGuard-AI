import math
import re
from urllib.parse import urlparse

from tld import get_fld, get_tld


TRUSTED_TLDS = {
    ".com",
    ".org",
    ".net",
    ".edu",
    ".gov",
    ".mil",
    ".int",
}

SUSPICIOUS_PATH_KEYWORDS = (
    "account",
    "auth",
    "bank",
    "billing",
    "confirm",
    "credential",
    "invoice",
    "login",
    "password",
    "payment",
    "reset",
    "secure",
    "signin",
    "update",
    "verify",
    "wallet",
)


def clean_url(url):
    """Clean whitespace from a URL."""
    return str(url).strip()


def compute_entropy(text):
    """Calculate Shannon entropy of a string."""

    if not text:
        return 0.0

    probabilities = [
        text.count(character) / len(text)
        for character in set(text)
    ]

    return -sum(
        probability * math.log2(probability)
        for probability in probabilities
    )


def extract_features(url):
    """Extract the 16 URL features used by the PhishTrap dataset."""

    original_url = clean_url(url).lower()

    url_string = original_url

    if not url_string.startswith("http"):
        url_string = "http://" + url_string

    parsed = urlparse(url_string)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    registered_domain = get_fld(
        url_string,
        fail_silently=True,
    ) or ""
    registered_tld = get_tld(
        url_string,
        fail_silently=True,
    ) or ""
    registered_label = (
        registered_domain[:-(len(registered_tld) + 1)]
        if registered_tld and registered_domain
        else ""
    )

    features = {}

    # 1. URL length
    features["url_length"] = len(url_string)

    # 2. Hyphen count
    features["hyphen_count"] = url_string.count("-")

    # 3. Digit count
    features["digit_count"] = sum(
        1 for character in url_string
        if character.isdigit()
    )

    # 4. Subdomain count
    features["subdomain_count"] = max(
        0,
        len(hostname.split(".")) - 2
    )

    # 5. Trusted TLD
    try:
        tld_info = get_tld(
            url_string,
            fail_silently=True
        )

        features["trusted_tld"] = int(
            tld_info is not None
            and f".{tld_info}" in TRUSTED_TLDS
        )

    except Exception:
        features["trusted_tld"] = 0

    # 6. Protocol exists
    features["protocol_exists"] = int(
        re.match(
            r"^https?://",
            original_url
        ) is not None
    )

    # 7. Special character count
    special_characters = "@-_.,;:#~!$&'()*+/:=?"

    features["special_char_count"] = sum(
        1
        for character in url_string
        if character in special_characters
    )

    # 8. URL entropy
    features["entropy"] = compute_entropy(url_string)

    # 9. Path depth
    features["path_depth"] = len(
        [
            part
            for part in path.split("/")
            if part
        ]
    )

    # 10. Domain length
    features["domain_length"] = len(hostname)

    # 11. IP address domain
    features["is_domain_ip"] = int(
        re.match(
            r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
            hostname
        ) is not None
    )

    # 12. @ symbol
    features["has_at_symbol"] = int(
        "@" in url_string
    )

    # 13. Double-slash redirect
    features["has_double_slash_redirect"] = int(
        url_string.count("//") > 1
    )

    # 14. TLD length
    try:
        tld_part = get_tld(
            url_string,
            fail_silently=True
        )

        features["tld_length"] = (
            len(tld_part)
            if tld_part
            else 0
        )

    except Exception:
        features["tld_length"] = 0

    # 15. Query parameter count
    features["query_param_count"] = (
        len(parsed.query.split("&"))
        if parsed.query
        else 0
    )

    # 16. Path length
    features["path_length"] = len(path)

    # Hostname-only and registrable-domain signals separate domain structure
    # from path and query complexity.
    features["hostname_entropy"] = compute_entropy(hostname)
    features["domain_digit_ratio"] = (
        sum(character.isdigit() for character in registered_label)
        / len(registered_label)
        if registered_label
        else 0.0
    )
    features["path_digit_ratio"] = (
        sum(character.isdigit() for character in path) / len(path)
        if path
        else 0.0
    )
    features["query_length"] = len(query)
    features["hostname_hyphen_count"] = hostname.count("-")
    features["domain_token_count"] = len(
        re.findall(r"[a-z0-9]+", registered_label)
    )
    features["suspicious_keyword_count"] = sum(
        len(
            re.findall(
                rf"(?<![a-z]){re.escape(keyword)}(?![a-z])",
                path + "?" + query,
            )
        )
        for keyword in SUSPICIOUS_PATH_KEYWORDS
    )
    features["percent_encoded_count"] = len(
        re.findall(r"%[0-9a-f]{2}", url_string)
    )
    features["punycode_detected"] = int(
        any(label.startswith("xn--") for label in hostname.split("."))
    )
    features["registered_domain_length"] = len(registered_domain)

    return features