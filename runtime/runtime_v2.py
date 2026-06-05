# LATS P3
# Runtime V4
#
# Purpose:
# - Integrate Market Brain + Memory Brain API + Trading Brain
# - Runtime talks to MemoryAPI as single public entry point
# - Runtime does not call Memory Brain internals directly
#
# Scope:
# - TEST only
# - No AI Chief
# - No Risk Brain
# - No Execution Brain

import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]

sys.path.append(str(BASE / "market_brain" / "logic"))
sys.path.append(str(BASE / "memory_brain" / "logic"))
sys.path.append(str(BASE / "trading_brain" / "logic"))

from build_market_context_v2 import build_market_context
from memory_from_chain import build_memory_record
from memory_api import MemoryAPI
from trading_brain_v2 import run_trading_brain


def build_query_from_context(context):
    return {
        "symbol": context.get("symbol"),
        "trend": context.get("trend"),
        "cycle": context.get("cycle"),
    }


def build_memory_match(routed_memory):
    return {
        "best_memory": routed_memory,
        "score": routed_memory.get("match_score", 0),
        "source": routed_memory.get("memory_source", ""),
        "status": routed_memory.get("status", ""),
    }


def summarize_top_memory(results):
    summary = []

    for memory in results:
        summary.append(
            {
                "memory_id": memory.get("memory_id"),
                "query_score": memory.get("query_score"),
                "hit_count": memory.get("hit_count", 0),
                "confirmed_count": memory.get("confirmed_count", 0),
                "status": memory.get("status", ""),
            }
        )

    return summary


def run():
    memory_api = MemoryAPI()

    context = build_market_context()

    memory_record = build_memory_record(
        context["chain"]
    )

    routed_memory = memory_api.route(
        memory_record
    )

    query = build_query_from_context(context)

    top_memory_results = memory_api.query(
        query,
        top_n=3,
        confirmed_only=True,
    )

    memory_match = build_memory_match(
        routed_memory
    )

    trade_decision = run_trading_brain(
        context,
        memory_match,
    )

    return {
        "runtime_version": "v4",
        "memory_api": memory_api.info(),

        "signal_id": context.get("signal_id"),
        "symbol": context.get("symbol"),
        "chain_id": context.get("chain", {}).get("chain_id"),
        "trend": context.get("trend"),
        "cycle": context.get("cycle"),

        "memory_source": routed_memory.get("memory_source"),
        "memory_status": routed_memory.get("status"),
        "memory_score": routed_memory.get("match_score"),

        "top_memory_results": summarize_top_memory(
            top_memory_results
        ),

        "trade_decision": trade_decision.get("decision"),
        "play_action": trade_decision.get("play_action"),
        "execution_mode": trade_decision.get("execution_mode"),
    }


if __name__ == "__main__":
    print(run())
