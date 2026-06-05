# ============================================================
# FILE: market_brain/logic/cycle.py
# LATS V3 V1
# Market Brain - Cycle Logic
#
# 4H = Cycle Context
# Logic copied/refactored from LATS V2 context_builder.py
# ============================================================

from typing import Dict, Any


def safe_str(value, default="unknown") -> str:
    if value is None or value == "":
        return default
    return str(value)


def interpret_cycle(snapshot: Dict[str, Any]) -> str:
    """
    Cycle = Phase
    ใช้ 4H เป็นแกนหลักของรอบตลาด
    """

    h4 = safe_str(snapshot.get("history_4h")).lower()
    h1 = safe_str(snapshot.get("history_1h")).lower()

    if h4 in ["up", "strong_up", "continuation"] and h1 in ["up", "strong_up"]:
        return "continue_up"

    if h4 in ["down", "strong_down", "continuation_down"] and h1 in ["down", "strong_down"]:
        return "continue_down"

    if h4 in ["up", "strong_up", "continuation"] and h1 in ["sideway", "pullback", "down"]:
        return "pullback_in_uptrend"

    if h4 in ["down", "strong_down", "continuation_down"] and h1 in ["sideway", "rebound", "up"]:
        return "rebound_in_downtrend"

    if h4 in ["sideway", "range", "flat"]:
        return "sideway_cycle"

    return "unknown_cycle"


if __name__ == "__main__":
    sample_snapshot = {
        "history_4h": "continuation",
        "history_1h": "up",
    }

    print(interpret_cycle(sample_snapshot))
