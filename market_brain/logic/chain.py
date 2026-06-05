# ============================================================
# FILE: market_brain/logic/chain.py
# LATS V3 V1
# Market Brain - Chain Logic
#
# History -> Story
# ============================================================

from typing import Dict, Any


def safe_str(value, default="unknown") -> str:
    if value is None or value == "":
        return default
    return str(value)


def build_chain(snapshot: Dict[str, Any]) -> str:
    """
    Chain = Story / History
    ย่อ History 15m + 1H + 4H เป็นเรื่องราวเดียว
    """

    h15 = safe_str(snapshot.get("history_15m")).lower()
    h1 = safe_str(snapshot.get("history_1h")).lower()
    h4 = safe_str(snapshot.get("history_4h")).lower()
    zone = safe_str(snapshot.get("zone")).lower()
    signal_type = safe_str(snapshot.get("signal_type")).lower()

    return f"{h4}>{h1}>{h15}>{zone}>{signal_type}"


if __name__ == "__main__":
    sample_snapshot = {
        "history_15m": "pullback",
        "history_1h": "up",
        "history_4h": "continuation",
        "zone": "support",
        "signal_type": "LONG",
    }

    print(build_chain(sample_snapshot))
