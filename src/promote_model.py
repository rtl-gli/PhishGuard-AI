import os
import shutil
import tempfile
from pathlib import Path

import joblib

from src.project import (
    BASE_FEATURE_COLUMNS,
    CANDIDATE_MODEL_PATH,
    DATASET_REVISION,
    MODEL_PATH,
)


def main():
    if not CANDIDATE_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Candidate model not found: {CANDIDATE_MODEL_PATH}. "
            "Run 'python -m src.train' and evaluate it first."
        )

    candidate = joblib.load(CANDIDATE_MODEL_PATH)
    if candidate.get("features") != BASE_FEATURE_COLUMNS:
        raise ValueError(
            "The candidate feature schema is not the validated 16-feature set."
        )
    if candidate.get("dataset_revision") != DATASET_REVISION:
        raise ValueError(
            "The candidate was not trained from the pinned PhishTrap revision."
        )
    if candidate.get("hard_negative_rows") != 1000:
        raise ValueError(
            "The candidate does not contain the expected hard-negative set."
        )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=MODEL_PATH.parent,
            prefix="phishing_model_",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temp_path = Path(temporary_file.name)
        shutil.copyfile(CANDIDATE_MODEL_PATH, temp_path)
        os.replace(temp_path, MODEL_PATH)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

    print(f"Promoted validated candidate to {MODEL_PATH}")
    print(f"Dataset revision: {DATASET_REVISION}")
    print(f"Features: {len(candidate['features'])}")
    print(f"Hard-negative training rows: {candidate['hard_negative_rows']}")


if __name__ == "__main__":
    main()
