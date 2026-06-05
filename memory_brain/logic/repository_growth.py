# LATS V3
# Repository Growth V1

import json
from pathlib import Path

BASE = Path.home() / "LATS_PRODUCTION_P3_TEST"

SNAPSHOT_DIR = (
    BASE /
    "memory_brain" /
    "data" /
    "snapshots"
)


def get_snapshots():
    if not SNAPSHOT_DIR.exists():
        return []

    return sorted(
        SNAPSHOT_DIR.glob(
            "memory_index_snapshot_*.json"
        )
    )


def load_snapshot(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def count_confirmed(memories):
    return sum(
        1
        for m in memories
        if m.get("status") == "confirmed"
    )


def count_candidate(memories):
    return sum(
        1
        for m in memories
        if m.get("status") == "waiting_confirm"
    )


def repository_growth():
    snapshots = get_snapshots()

    if len(snapshots) < 2:
        return {
            "status": "WAITING_MORE_SNAPSHOTS",
            "snapshot_count": len(snapshots),
        }

    old = load_snapshot(snapshots[-2])
    new = load_snapshot(snapshots[-1])

    old_memories = old.get("memories", [])
    new_memories = new.get("memories", [])

    return {
        "status": "OK",

        "old_total": len(old_memories),
        "new_total": len(new_memories),
        "growth_total":
            len(new_memories)
            - len(old_memories),

        "old_confirmed":
            count_confirmed(old_memories),

        "new_confirmed":
            count_confirmed(new_memories),

        "growth_confirmed":
            count_confirmed(new_memories)
            - count_confirmed(old_memories),

        "old_candidate":
            count_candidate(old_memories),

        "new_candidate":
            count_candidate(new_memories),

        "growth_candidate":
            count_candidate(new_memories)
            - count_candidate(old_memories),
    }


if __name__ == "__main__":
    print(repository_growth())
