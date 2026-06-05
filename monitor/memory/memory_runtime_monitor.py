# LATS P3
# Memory Runtime Monitor V1
#
# Purpose:
# - Display Memory Brain runtime status
# - Read through MemoryAPI
# - Monitor only, no write action
#
# Scope:
# - TEST only
# - No AI Chief
# - No Risk Brain
# - No Execution Brain

import sys
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"
LOGIC = ROOT / "memory_brain" / "logic"
RUNTIME = ROOT / "runtime"

sys.path.insert(0, str(LOGIC))
sys.path.insert(0, str(RUNTIME))

from memory_api import MemoryAPI
from runtime_v2 import run


def short(value, width=28):
    text = str(value or "")
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def line():
    print("─" * 72)


def title(text):
    print("┌" + "─" * 70 + "┐")
    print("│" + text.center(70) + "│")
    print("└" + "─" * 70 + "┘")


def row(left, right):
    print(f"{left:<34} {right}")


def show_memory_section(api):
    health = api.health()
    stats = api.stats()
    candidate_stats = api.candidate_stats()

    title("LATS P3 MEMORY RUNTIME MONITOR")

    row("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    row("Memory API", api.info().get("status"))
    row("Health", health.get("status"))

    line()

    row("Total Memory", health.get("total_memory"))
    row("Confirmed", stats.get("confirmed_memory"))
    row("Candidate In Repository", stats.get("candidate_memory"))
    row("Candidate Workflow", candidate_stats.get("total_candidates"))
    row("Rejected", stats.get("rejected_memory"))
    row("Missing Examples", health.get("missing_examples"))
    row("Duplicate IDs", health.get("duplicate_ids"))

    line()

    top_hit = stats.get("top_hit_memory", [])

    if not top_hit:
        row("Top Memory", "NONE")
        return

    best = top_hit[0]

    row("Top Memory ID", short(best.get("memory_id")))
    row("Top Hit Count", best.get("hit_count"))
    row("Top Confirmed Count", best.get("confirmed_count"))
    row("Top Example Count", best.get("example_count"))


def show_runtime_section():
    line()
    title("LAST RUNTIME DECISION")

    try:
        result = run()
    except Exception as exc:
        row("Runtime Status", "ERROR")
        row("Error", short(exc, 60))
        return

    row("Runtime Version", result.get("runtime_version"))
    row("Symbol", result.get("symbol"))
    row("Signal ID", short(result.get("signal_id"), 40))
    row("Chain ID", short(result.get("chain_id"), 40))
    row("Trend", result.get("trend"))
    row("Cycle", result.get("cycle"))

    line()

    row("Memory Source", result.get("memory_source"))
    row("Memory Status", result.get("memory_status"))
    row("Memory Score", result.get("memory_score"))

    line()

    row("Trade Decision", result.get("trade_decision"))
    row("Play Action", result.get("play_action"))
    row("Execution Mode", result.get("execution_mode"))

    line()

    top = result.get("top_memory_results", [])

    if not top:
        row("Top Memory Results", "NONE")
        return

    row("Top Memory Results", len(top))

    for i, item in enumerate(top[:3], start=1):
        row(
            f"Top {i}",
            f"{short(item.get('memory_id'), 32)} "
            f"score={item.get('query_score')} "
            f"hit={item.get('hit_count')}",
        )


def main():
    api = MemoryAPI()
    show_memory_section(api)
    show_runtime_section()


if __name__ == "__main__":
    main()
