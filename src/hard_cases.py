import random
from urllib.parse import urlencode, urlsplit, urlunsplit

import pandas as pd
from tld import get_fld

from src.features import extract_features
from src.project import FEATURE_COLUMNS


LEGITIMATE_URL_TEMPLATES = (
    (
        "/products/category/home-audio/wireless-headphones/model-2026",
        (
            ("utm_source", "weekly_newsletter"),
            ("utm_medium", "email"),
            ("utm_campaign", "spring_collection"),
            ("ref", "category_navigation"),
        ),
    ),
    (
        "/search",
        (
            ("q", "wireless headphones noise cancelling"),
            ("category", "electronics"),
            ("sort", "price"),
            ("page", "2"),
            ("filter", "available"),
            ("source", "site_navigation"),
        ),
    ),
    (
        "/news/technology/2026/09/26/how-to-compare-devices",
        (
            ("utm_source", "homepage"),
            ("utm_medium", "referral"),
            ("utm_campaign", "technology_digest"),
            ("article", "20260926"),
        ),
    ),
    (
        "/catalog/electronics/audio/headphones/wireless/model-2026/variant-123456",
        (
            ("color", "black"),
            ("size", "large"),
            ("availability", "in_stock"),
            ("region", "gb"),
            ("currency", "gbp"),
        ),
    ),
    (
        "/help/ordering/delivery-and-returns",
        (
            ("utm_source", "support"),
            ("utm_medium", "footer"),
            ("utm_campaign", "customer_help"),
            ("session", "12345678"),
        ),
    ),
)


def _hostname_and_registrable_domain(url: str) -> tuple[str, str]:
    candidate = url if "://" in url else f"https://{url}"
    parsed = urlsplit(candidate)
    hostname = parsed.hostname or ""
    registrable_domain = get_fld(candidate, fail_silently=True) or ""
    return hostname, registrable_domain


def generate_complex_legitimate_urls(
    legitimate_urls: pd.Series,
    max_domains: int = 200,
) -> list[str]:
    """Generate structural hard negatives from known legitimate domains."""
    domains = set()
    for url in legitimate_urls.dropna().astype(str):
        hostname, registrable_domain = _hostname_and_registrable_domain(url)
        if hostname and registrable_domain:
            domains.add(hostname)

    ordered_domains = sorted(domains)
    selected_domains = random.Random(42).sample(
        ordered_domains,
        min(max_domains, len(ordered_domains)),
    )
    generated = []
    for hostname in selected_domains:
        for path, query_items in LEGITIMATE_URL_TEMPLATES:
            generated.append(
                urlunsplit(
                    (
                        "https",
                        hostname,
                        path,
                        urlencode(query_items),
                        "",
                    )
                )
            )
    return generated


def build_feature_frame(urls: list[str], label: int) -> pd.DataFrame:
    rows = [extract_features(url) for url in urls]
    frame = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    frame["label"] = label
    frame["url"] = urls
    return frame
