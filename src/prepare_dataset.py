import json
from pathlib import Path

from sklearn.model_selection import StratifiedGroupKFold

from src.domains import registrable_domain
from src.project import (
    DATASET_REVISION,
    DATASET_SHA256,
    PROJECT_ROOT,
    load_dataset,
)


SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
SPLIT_COUNT = 20


def main():
    dataset = load_dataset()
    groups = dataset["url"].map(registrable_domain)
    fold_ids = [-1] * len(dataset)
    splitter = StratifiedGroupKFold(
        n_splits=SPLIT_COUNT,
        shuffle=True,
        random_state=42,
    )

    for fold_id, (_, held_out_indices) in enumerate(
        splitter.split(dataset, dataset["label"], groups)
    ):
        for index in held_out_indices:
            fold_ids[index] = fold_id

    if any(fold_id < 0 for fold_id in fold_ids):
        raise RuntimeError("Group-stratified split did not assign every row.")

    train_mask = [fold_id >= 6 for fold_id in fold_ids]
    validation_mask = [3 <= fold_id < 6 for fold_id in fold_ids]
    test_mask = [fold_id < 3 for fold_id in fold_ids]
    partitions = {
        "train": dataset.loc[train_mask],
        "val": dataset.loc[validation_mask],
        "test": dataset.loc[test_mask],
    }

    group_sets = {
        name: set(partition["url"].map(registrable_domain))
        for name, partition in partitions.items()
    }
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        overlap = group_sets[left] & group_sets[right]
        if overlap:
            raise RuntimeError(
                f"Registrable-domain leakage remains between {left} and {right}."
            )

    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    for name, partition in partitions.items():
        output_path = SPLITS_DIR / f"{name}.csv"
        partition.to_csv(output_path, index=False)
        counts = partition["label"].value_counts().sort_index().to_dict()
        print(
            f"{name}: {len(partition)} rows, labels={counts}, "
            f"registrable domains={len(group_sets[name])}"
        )
        print(f"  wrote {output_path}")

    manifest = {
        "dataset": "saidutta69/PhishTrap",
        "revision": DATASET_REVISION,
        "source_sha256": DATASET_SHA256,
        "split_method": "StratifiedGroupKFold",
        "fold_count": SPLIT_COUNT,
        "random_state": 42,
        "fold_assignment": {
            "test": "folds 0-2",
            "validation": "folds 3-5",
            "train": "folds 6-19",
        },
        "rows": {
            name: len(partition)
            for name, partition in partitions.items()
        },
        "registrable_domains": {
            name: len(group_sets[name])
            for name in group_sets
        },
    }
    (SPLITS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print("No registrable domain appears in more than one split.")


if __name__ == "__main__":
    main()
