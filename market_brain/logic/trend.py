# ============================================================
# FILE: market_brain/logic/trend.py
# LATS V3 V1
# Market Brain - Trend Logic
#
# 1H = Trend Context
# Logic copied/refactored from LATS V2 context_builder.py
# ============================================================

from typing import Dict, Any


def safe_str(value, default="unknown") -> str:
    if value is None or value == "":
        return default
    return str(value)


def interpret_trend(snapshot: Dict[str, Any]) -> str:
    """
    Trend = Direction
    ใช้ 1H เป็นแกนหลักของทิศทาง
    """

    h1 = safe_str(snapshot.get("history_1h")).lower()

    if h1 in ["up", "strong_up", "bullish"]:
        return "up"

    if h1 in ["down", "strong_down", "bearish"]:
        return "down"

    if h1 in ["sideway", "flat", "range"]:
        return "sideway"

    return "unknown"


if __name__ == "__main__":
    sample_snapshot = {
        "history_1h": "up",
    }

    print(interpret_trend(sample_snapshot))
