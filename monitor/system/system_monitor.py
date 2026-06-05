# LATS V3
# NOC System Monitor V1

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE / "memory_brain" / "logic"))

from memory_health import check_memory_health
from repository_stats import build_repository_stats


def status_icon(status):
    return "OK" if status == "OK" else "WARN"


def print_system_monitor():
    memory_health = check_memory_health()
    memory_stats = build_repository_stats()

    print("=" * 70)
    print("LATS NOC - SYSTEM MONITOR")
    print("=" * 70)

    print("CORE SYSTEM")
    print("-" * 70)
    print("Network      : TODO")
    print("Server       : TODO")
    print("Database     :", status_icon(memory_health.get("status")))
    print("Application  : TODO")
    print("Security     : TODO")
    print("Alert        : TODO")
    print("Business     : OK")

    print("-" * 70)
    print("DATABASE / MEMORY")
    print("-" * 70)
    print(f"Memory Total     : {memory_stats.get('total_memory')}")
    print(f"Confirmed Memory : {memory_stats.get('confirmed_memory')}")
    print(f"Candidate Memory : {memory_stats.get('candidate_memory')}")
    print(f"Avg Examples     : {memory_stats.get('avg_examples')}")

    print("-" * 70)
    print("NEXT DRILL DOWN")
    print("-" * 70)
    print("Database Detail:")
    print("python3 ~/LATS_PRODUCTION_P3_TEST/monitor/database/repository_operations_monitor.py")

    print("=" * 70)


if __name__ == "__main__":
    print_system_monitor()
