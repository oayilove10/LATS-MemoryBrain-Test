# LATS V3 V1
# Trading Brain - Weight Engine

import csv
import os


def load_weights(weight_file: str) -> dict:
    if not os.path.exists(weight_file):
        return {}

    weights = {}

    with open(weight_file, "r", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)

        for row in rows:
            memory_id = row.get("memory_id", "")
            try:
                weights[memory_id] = float(row.get("memory_weight", 1.0))
            except Exception:
                weights[memory_id] = 1.0

    return weights


def get_weight(memory_id: str, weights: dict, default: float = 1.0) -> float:
    return float(weights.get(memory_id, default))


if __name__ == "__main__":
    print(get_weight("TEST_MEMORY", {}, 1.0))
