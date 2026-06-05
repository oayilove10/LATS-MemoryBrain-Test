# LATS V3 V1
# Memory Store

import json
from pathlib import Path


BASE = Path.home() / "LATS_PRODUCTION_P3_TEST"

MEMORY_DIR = (
    BASE /
    "memory_brain" /
    "data"
)

MEMORY_FILE = (
    MEMORY_DIR /
    "chain_memory.json"
)


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory_list):
    MEMORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            memory_list,
            f,
            ensure_ascii=False,
            indent=2,
        )


def append_memory(memory_record):
    memory_list = load_memory()
    memory_list.append(memory_record)
    save_memory(memory_list)

    return MEMORY_FILE


if __name__ == "__main__":
    record = {
        "memory_id": "MEM_TEST",
        "symbol": "BTCUSDT",
        "chain_id": "CHAIN_TEST",
        "trend": "up",
        "cycle": "continue_up",
        "result": "",
        "status": "candidate",
    }

    path = append_memory(record)

    print(path)
