# LATS V3
# Repository Monitor V1

from repository_stats import build_repository_stats
from memory_health import check_memory_health


def print_repository_monitor():
    stats = build_repository_stats()
    health = check_memory_health()

    print("=" * 60)
    print("LATS MEMORY REPOSITORY MONITOR")
    print("=" * 60)

    print(f"Total Memory      : {stats['total_memory']}")
    print(f"Confirmed Memory  : {stats['confirmed_memory']}")
    print(f"Candidate Memory  : {stats['candidate_memory']}")
    print(f"Avg Examples      : {stats['avg_examples']}")
    print(f"Health Status     : {health['status']}")

    print("-" * 60)
    print("TOP HIT MEMORY")
    print("-" * 60)

    for i, item in enumerate(stats["top_hit_memory"], start=1):
        print(
            f"{i}. {item['memory_id']} | hit_count={item['hit_count']}"
        )

    print("-" * 60)
    print("TOP CONFIRMED MEMORY")
    print("-" * 60)

    for i, item in enumerate(stats["top_confirmed_memory"], start=1):
        print(
            f"{i}. {item['memory_id']} | confirmed_count={item['confirmed_count']}"
        )

    print("=" * 60)


if __name__ == "__main__":
    print_repository_monitor()
