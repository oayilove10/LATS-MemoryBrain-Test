# ============================================================
# FILE: market_brain/logic/market_brain.py
# LATS V3 V1
# Market Brain Aggregator
# Trend + Cycle + Chain + Event -> Market Context
# ============================================================

from typing import Dict, Any

from trend import interpret_trend
from cycle import interpret_cycle
from chain import build_chain
from event import build_event


def build_market_context(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    event = build_event(snapshot)

    return {
        "signal_id": snapshot.get("signal_id", ""),
        "symbol": snapshot.get("symbol", ""),
        "trend_1h": interpret_trend(snapshot),
        "cycle_4h": interpret_cycle(snapshot),
        "chain": build_chain(snapshot),
        "event": event,
    }


if __name__ == "__main__":
    sample_snapshot = {
        "signal_id": "BTCUSDT_15m_1748112300000",
        "symbol": "BTCUSDT",
        "signal_type": "LONG",
        "history_15m": "pullback",
        "history_1h": "up",
        "history_4h": "continuation",
        "zone": "support",
        "timeframe": "15m",
        "event_type": "15m_SIGNAL",
        "event_time": "2026-06-03 09:15:00",
    }

    print(build_market_context(sample_snapshot))
