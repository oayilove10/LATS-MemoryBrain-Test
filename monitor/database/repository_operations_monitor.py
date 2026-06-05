# LATS V3
# NOC Database Monitor - Memory Repository Operations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE / "memory_brain" / "logic"))

from memory_health import check_memory_health
from repository_stats import build_repository_stats
from repository_growth import repository_growth


def print_operations_monitor():
    health = check_memory_health()
    stats = build_repository_stats()
    growth = repository_growth()

    print("=" * 70)
    print("LATS NOC - DATABASE / MEMORY REPOSITORY")
    print("=" * 70)

    print(f"Health Status     : {health.get('status')}")
    print(f"Total Memory      : {stats.get('total_memory')}")
    print(f"Confirmed Memory  : {stats.get('confirmed_memory')}")
    print(f"Candidate Memory  : {stats.get('candidate_memory')}")
    print(f"Avg Examples      : {stats.get('avg_examples')}")

    print("-" * 70)
    print("GROWTH")
    print("-" * 70)
    print(f"Growth Status     : {growth.get('status')}")
    print(f"Old Total         : {growth.get('old_total', '-')}")
    print(f"New Total         : {growth.get('new_total', '-')}")
    print(f"Growth Total      : {growth.get('growth_total', '-')}")
    print(f"Growth Confirmed  : {growth.get('growth_confirmed', '-')}")
    print(f"Growth Candidate  : {growth.get('growth_candidate', '-')}")

    print("-" * 70)
    print("TOP HIT MEMORY")
    print("-" * 70)
    for i, item in enumerate(stats.get("top_hit_memory", []), start=1):
        print(f"{i}. {item.get('memory_id')} | hit_count={item.get('hit_count')}")

    print("-" * 70)
    print("TOP CONFIRMED MEMORY")
    print("-" * 70)
    for i, item in enumerate(stats.get("top_confirmed_memory", []), start=1):
        print(f"{i}. {item.get('memory_id')} | confirmed_count={item.get('confirmed_count')}")

    print("=" * 70)


if __name__ == "__main__":
    print_operations_monitor()
