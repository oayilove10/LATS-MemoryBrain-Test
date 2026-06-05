# LATS V3 V1
# Runtime Main

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

sys.path.append(str(BASE / "market_brain" / "logic"))
sys.path.append(str(BASE / "trading_brain" / "logic"))
sys.path.append(str(BASE / "ai_chief" / "logic"))
sys.path.append(str(BASE / "raw_database" / "snapshots"))

from market_brain import build_market_context
from trading_brain import run_trading_brain
from ai_chief import run_ai_chief
from load_snapshot import load_latest_snapshot
from memory_loader import (
    load_best_memory,
    convert_memory_for_similarity,
)


def main():
    snapshot = load_latest_snapshot()

    market_context = build_market_context(snapshot)

    signal = {
        "cycle": market_context["cycle_4h"],
        "trend": market_context["trend_1h"],
        "zone": snapshot["zone"],
        "direction": snapshot["signal_type"].lower(),
        "symbol": snapshot["symbol"],
        "pattern": snapshot["history_15m"],
    }

    best_memory = load_best_memory()
    memory = convert_memory_for_similarity(best_memory)

    weights = {
        memory["memory_id"]: memory["weight"]
    }

    trade_decision = run_trading_brain(
        signal,
        memory,
        weights,
    )

    final_decision = run_ai_chief(
        market_context,
        trade_decision,
    )

    print(final_decision)


if __name__ == "__main__":
    main()


