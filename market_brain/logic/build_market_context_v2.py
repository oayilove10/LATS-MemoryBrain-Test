# LATS V3 V1
# Market Context Builder V2

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE / "raw_database" / "snapshots"))
sys.path.append(str(BASE / "market_brain" / "logic"))

from load_snapshot import load_latest_snapshot
from event import build_event
from chain_builder import build_chain_record
from trend_from_chain import detect_trend
from cycle_from_chain import detect_cycle


def build_market_context():
    snapshot = load_latest_snapshot()

    signal_event = build_event(snapshot)

    events = [
        {
            "symbol": snapshot.get("symbol", ""),
            "timeframe": "4H",
            "event_type": "4H_BULL_CLOSE",
            "event_time": "2026-06-03 08:00:00",
        },
        {
            "symbol": snapshot.get("symbol", ""),
            "timeframe": "1H",
            "event_type": "1H_BULL_CLOSE",
            "event_time": "2026-06-03 09:00:00",
        },
        signal_event,
    ]

    chain = build_chain_record(events)

    trend = detect_trend(chain)
    cycle = detect_cycle(chain)

    chain["trend"] = trend
    chain["cycle"] = cycle

    return {
        "signal_id": snapshot.get("signal_id", ""),
        "symbol": snapshot.get("symbol", ""),
        "events": events,
        "chain": chain,
        "trend": trend,
        "cycle": cycle,
    }


if __name__ == "__main__":
    print(build_market_context())
