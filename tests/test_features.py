import pandas as pd

from src.domains import registrable_domain
from src.features import compute_entropy, extract_features
from src.hard_cases import generate_complex_legitimate_urls


def test_entropy_empty_string():
    assert compute_entropy("") == 0.0


def test_entropy_non_empty_string():
    entropy = compute_entropy("aaaa")
    assert entropy == 0.0


def test_legitimate_url_features():
    features = extract_features("http://ucweb.com")

    assert features["url_length"] == 16
    assert features["hyphen_count"] == 0
    assert features["digit_count"] == 0
    assert features["subdomain_count"] == 0
    assert features["trusted_tld"] == 1
    assert features["protocol_exists"] == 1
    assert features["is_domain_ip"] == 0
    assert features["has_at_symbol"] == 0


def test_suspicious_url_features():
    features = extract_features(
        "http://rrakuten.co.jp.lbtte.xyz"
    )

    assert features["subdomain_count"] == 3
    assert features["trusted_tld"] == 0
    assert features["protocol_exists"] == 1
    assert features["is_domain_ip"] == 0


def test_url_without_protocol():
    features = extract_features("ucweb.com")

    assert features["protocol_exists"] == 0
    assert features["domain_length"] == 9


def test_ip_address_detection():
    features = extract_features(
        "http://192.168.1.1"
    )

    assert features["is_domain_ip"] == 1


def test_at_symbol_detection():
    features = extract_features(
        "http://example.com@evil.com"
    )

    assert features["has_at_symbol"] == 1


def test_query_parameters():
    features = extract_features(
        "http://example.com/login?user=123&id=456"
    )

    assert features["query_param_count"] == 2


def test_https_and_redirect_pattern_detection():
    features = extract_features("https://example.com//evil")

    assert features["protocol_exists"] == 1
    assert features["has_double_slash_redirect"] == 1
    assert features["path_depth"] == 1


def test_long_url_and_many_query_parameters():
    url = "https://example.com/login?" + "&".join(
        f"key{index}=value" for index in range(5)
    )
    features = extract_features(url)

    assert features["query_param_count"] == 5
    assert features["path_length"] == 6


def test_hostname_path_and_query_features_are_separate():
    features = extract_features(
        "https://sub.example.co.uk/verify/55?next=%2Fhome"
    )

    assert features["hostname_entropy"] == compute_entropy("sub.example.co.uk")
    assert features["domain_digit_ratio"] == 0
    assert features["path_digit_ratio"] == 0.2
    assert features["query_length"] == len("next=%2Fhome")
    assert features["hostname_hyphen_count"] == 0
    assert features["domain_token_count"] == 1
    assert features["suspicious_keyword_count"] == 1
    assert features["percent_encoded_count"] == 1
    assert features["punycode_detected"] == 0
    assert features["registered_domain_length"] == len("example.co.uk")


def test_domain_digit_ratio_and_hostname_hyphens():
    features = extract_features("https://bank-2.example.com/path123")

    assert features["domain_digit_ratio"] == 0
    assert features["hostname_hyphen_count"] == 1
    assert features["path_digit_ratio"] == 3 / len("/path123")


def test_punycode_hostname_detection():
    features = extract_features("https://xn--bcher-kva.example/login")

    assert features["punycode_detected"] == 1


def test_registered_domain_digit_ratio_excludes_subdomains():
    features = extract_features("https://portal.bank2.com/home")

    assert features["domain_digit_ratio"] == 0.2
    assert features["registered_domain_length"] == len("bank2.com")


def test_registrable_domain_handles_multi_label_suffix():
    assert registrable_domain("https://shop.example.co.uk/products") == "example.co.uk"


def test_generated_hard_negatives_are_complex_but_remain_on_source_host():
    generated = generate_complex_legitimate_urls(
        pd.Series(["https://www.example.com"]),
        max_domains=1,
    )

    assert len(generated) == 5
    assert all(url.startswith("https://www.example.com/") for url in generated)
    assert any(extract_features(url)["query_param_count"] >= 4 for url in generated)
    assert any(extract_features(url)["path_depth"] >= 5 for url in generated)