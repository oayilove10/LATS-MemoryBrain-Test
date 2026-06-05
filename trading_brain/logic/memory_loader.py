# LATS V3 V1
# Trading Brain - Memory Loader
# Read Memory V3 latest full brain export

import json
from pathlib import Path


MEMORY_FILE = (
    Path.home()
    / "LATS_PRODUCTION"
    / "data/memory_v3/full_brain_exports/latest_full_brain_decision.json"
)


def load_best_memory():
    if not MEMORY_FILE.exists():
        return {}

    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("best_memory", {})


def infer_cycle(group: str) -> str:
    group = str(group or "").lower()

    if "continue_long" in group:
        return "continue_up"

    if "continue_short" in group:
        return "continue_down"

    if "breakout" in group and "long" in group:
        return "continue_up"

    if "breakout" in group and "short" in group:
        return "continue_down"

    return "unknown_cycle"


def infer_trend(direction: str) -> str:
    direction = str(direction or "").lower()

    if direction == "long":
        return "up"

    if direction == "short":
        return "down"

    return "unknown"


def convert_memory_for_similarity(best_memory):
    direction = str(best_memory.get("direction", "")).lower()
    group = str(best_memory.get("continuation_group", "")).lower()

    return {
        "memory_id": best_memory.get("memory_id", ""),
        "symbol": best_memory.get("symbol", ""),
        "cycle": infer_cycle(group),
        "trend": infer_trend(direction),
        "pattern": group,
        "direction": direction,
        "zone": best_memory.get("zone", ""),
        "similarity": best_memory.get("similarity", 0),
        "weight": best_memory.get("weight", 1.0),
        "final_score": best_memory.get("final_score", 0),
        "risk_note": best_memory.get("risk_note", ""),
    }


if __name__ == "__main__":
    best = load_best_memory()
    print(convert_memory_for_similarity(best))
