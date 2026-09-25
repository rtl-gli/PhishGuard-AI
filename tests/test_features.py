from src.features import compute_entropy, extract_features


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