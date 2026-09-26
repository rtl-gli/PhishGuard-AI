import argparse
from pathlib import Path

import pandas as pd

from src.hard_cases import generate_complex_legitimate_urls
from src.project import load_dataset_split


VALIDATION_DIR = Path(__file__).resolve().parent.parent / "data" / "validation"


def main():
    parser = argparse.ArgumentParser(
        description="Prepare local hard-case validation CSVs from the pinned dataset."
    )
    parser.add_argument(
        "--legitimate-url",
        help="Optional known-legitimate URL to include as an external hard case.",
    )
    args = parser.parse_args()

    validation = load_dataset_split("val")
    legitimate = validation.loc[validation["label"] == 0]
    phishing = validation.loc[validation["label"] == 1]

    safe_urls = generate_complex_legitimate_urls(
        legitimate["url"],
        max_domains=100,
    )
    legitimate_cases = pd.DataFrame(
        {
            "url": safe_urls,
            "label": 0,
            "provenance": "Tranco domain; representative path/query generated",
        }
    )
    if args.legitimate_url:
        legitimate_cases.loc[len(legitimate_cases)] = {
            "url": args.legitimate_url,
            "label": 0,
            "provenance": "User-supplied known-legitimate URL",
        }

    hardest_phishing = phishing.sort_values(
        [
            "is_domain_ip",
            "has_at_symbol",
            "protocol_exists",
            "trusted_tld",
            "url_length",
            "subdomain_count",
        ],
        ascending=[True, True, False, False, True, True],
    ).head(100)
    phishing_cases = hardest_phishing[["url", "label"]].copy()
    phishing_cases["provenance"] = (
        "PhishTrap pinned validation; HTTPS/trusted-TLD/non-IP/no-@ prioritized"
    )

    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    legitimate_cases.to_csv(
        VALIDATION_DIR / "legitimate_hard_cases.csv",
        index=False,
    )
    phishing_cases.to_csv(
        VALIDATION_DIR / "phishing_hard_cases.csv",
        index=False,
    )

    print(f"Legitimate hard cases written: {len(legitimate_cases)}")
    print(f"Phishing hard cases written: {len(phishing_cases)}")
    print(f"Local validation directory: {VALIDATION_DIR}")
    print("These CSVs contain URLs and are intentionally excluded from Git.")


if __name__ == "__main__":
    main()
