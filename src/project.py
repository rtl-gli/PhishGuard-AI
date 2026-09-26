import json
from hashlib import sha256
from pathlib import Path

import pandas as pd

from src.features import extract_features

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "phishtrap_full.csv"
DATASET_REVISION = "26dc2bff5f8c26346f26611bab102f8d0a0fc7c2"
DATASET_SHA256 = "2b66391ff8af4e63c35648b65b399a4c590ea094733dda00534174e11196fc3c"
DATA_SPLIT_PATHS = {
    "train": PROJECT_ROOT / "data" / "splits" / "train.csv",
    "val": PROJECT_ROOT / "data" / "splits" / "val.csv",
    "test": PROJECT_ROOT / "data" / "splits" / "test.csv",
}
DATA_SPLIT_MANIFEST_PATH = PROJECT_ROOT / "data" / "splits" / "manifest.json"
MODEL_PATH = PROJECT_ROOT / "model" / "phishing_model.pkl"
CANDIDATE_MODEL_PATH = PROJECT_ROOT / "model" / "phishing_model_candidate.pkl"

BASE_FEATURE_COLUMNS = [
    "url_length",
    "hyphen_count",
    "digit_count",
    "subdomain_count",
    "trusted_tld",
    "protocol_exists",
    "special_char_count",
    "entropy",
    "path_depth",
    "domain_length",
    "is_domain_ip",
    "has_at_symbol",
    "has_double_slash_redirect",
    "tld_length",
    "query_param_count",
    "path_length",
]

ADDITIONAL_FEATURE_COLUMNS = [
    "hostname_entropy",
    "domain_digit_ratio",
    "path_digit_ratio",
    "query_length",
    "hostname_hyphen_count",
    "domain_token_count",
    "suspicious_keyword_count",
    "percent_encoded_count",
    "punycode_detected",
    "registered_domain_length",
]


FEATURE_COLUMNS = BASE_FEATURE_COLUMNS + ADDITIONAL_FEATURE_COLUMNS


def _load_dataset_file(
    path: Path,
    expected_sha256: str | None = None,
) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            "Obtain the pinned PhishTrap CSV files and place them in data/raw/; "
            "raw datasets are intentionally excluded from Git."
        )
    if expected_sha256:
        actual_sha256 = sha256(path.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            raise ValueError(
                f"Dataset checksum mismatch for {path.name}: expected "
                f"{expected_sha256}, got {actual_sha256}."
            )

    dataset = pd.read_csv(path)
    required_columns = {"url", "label"}
    missing_columns = sorted(required_columns - set(dataset.columns))
    if missing_columns:
        raise ValueError(
            f"Dataset {path.name} is missing required columns: "
            f"{', '.join(missing_columns)}"
        )
    if dataset["url"].isna().any() or dataset["label"].isna().any():
        raise ValueError(f"Dataset {path.name} contains missing URLs or labels.")
    if not set(dataset["label"].unique()).issubset({0, 1}):
        raise ValueError(f"Dataset {path.name} labels must be 0 or 1.")

    derived_features = pd.DataFrame(
        [extract_features(url) for url in dataset["url"]],
        index=dataset.index,
    )
    for column in BASE_FEATURE_COLUMNS:
        if column in dataset:
            consistent = (
                (dataset[column] - derived_features[column]).abs() <= 1e-9
            ).all()
            if not consistent:
                raise ValueError(
                    f"Stored feature '{column}' does not match the runtime "
                    f"extractor in {path.name}."
                )

    dataset = dataset.drop(
        columns=[column for column in FEATURE_COLUMNS if column in dataset],
    )
    dataset = pd.concat([dataset, derived_features], axis=1)
    return dataset


def load_dataset() -> pd.DataFrame:
    dataset = _load_dataset_file(DATA_PATH, DATASET_SHA256)
    label_counts = dataset["label"].value_counts().to_dict()
    if len(dataset) != 19948 or label_counts != {0: 9974, 1: 9974}:
        raise ValueError(
            "The pinned PhishTrap snapshot must contain 19,948 rows "
            "with 9,974 examples per label."
        )
    return dataset


def load_dataset_split(split: str) -> pd.DataFrame:
    try:
        path = DATA_SPLIT_PATHS[split]
    except KeyError as error:
        allowed = ", ".join(DATA_SPLIT_PATHS)
        raise ValueError(
            f"Unknown dataset split '{split}'. Choose one of: {allowed}."
        ) from error

    if not path.exists():
        raise FileNotFoundError(
            f"Prepared dataset split not found: {path}. "
            "Run 'python -m src.prepare_dataset' after placing "
            "phishtrap_full.csv in data/raw/."
        )

    if not DATA_SPLIT_MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Prepared split manifest not found: {DATA_SPLIT_MANIFEST_PATH}. "
            "Run 'python -m src.prepare_dataset' to regenerate the splits."
        )
    manifest = json.loads(
        DATA_SPLIT_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    if (
        manifest.get("revision") != DATASET_REVISION
        or manifest.get("source_sha256") != DATASET_SHA256
    ):
        raise ValueError(
            "Prepared splits do not match the pinned PhishTrap snapshot. "
            "Run 'python -m src.prepare_dataset' again."
        )
    expected_rows = manifest.get("rows", {}).get(split)
    if not isinstance(expected_rows, int):
        raise ValueError(
            f"Prepared split manifest has no row count for '{split}'."
        )

    dataset = _load_dataset_file(path)
    if len(dataset) != expected_rows:
        raise ValueError(
            f"Prepared split {split} has {len(dataset)} rows; "
            f"the manifest specifies {expected_rows}."
        )
    return dataset
