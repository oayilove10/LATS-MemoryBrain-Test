# LATS V3
# Repository Stats V2
#
# Compatibility wrapper for old imports.
# Real statistics logic lives in repository_statistics.py

from repository_statistics import build_repository_statistics


def build_repository_stats():
    return build_repository_statistics(top_n=3)


if __name__ == "__main__":
    print(build_repository_stats())
