# LATS P3
# Memory API V2
#
# Public Entry Point for Memory Brain.
#
# Purpose:
# - Runtime / Monitor call this file only
# - Hide internal logic files
# - Keep Memory Brain clean before Runtime Integration
# - Provide route() so Runtime uses MemoryAPI 100%
#
# Scope:
# - No AI Chief
# - No Risk Brain
# - No Execution Brain
# - TEST only

from memory_repository import (
    get_all_memories,
    find_by_id,
    upsert,
)

from memory_search import (
    search_memory,
    search_confirmed_memory,
    search_candidate_memory,
)

from memory_query import (
    query_memory_index,
)

from repository_statistics import (
    build_repository_statistics,
)

from memory_health import (
    check_memory_health,
)

from candidate_repository import (
    upsert_candidate,
    find_candidate,
    list_candidates,
    mark_candidate_confirmed,
    mark_candidate_rejected,
    candidate_repository_stats,
)

from memory_promoter import (
    promote_memory,
)

from memory_index_router import (
    route_memory,
)


class MemoryAPI:
    def __init__(self):
        self.name = "LATS_P3_MEMORY_API"
        self.version = "v2"

    def info(self):
        return {
            "name": self.name,
            "version": self.version,
            "status": "OK",
            "scope": "memory_brain_only",
        }

    def all_memories(self):
        return get_all_memories()

    def find_memory(self, memory_id):
        return find_by_id(memory_id)

    def save_memory(self, memory):
        return upsert(memory)

    def route(self, memory_record):
        return route_memory(memory_record)

    def search(self, query, status_filter=None, min_score=100):
        return search_memory(
            query,
            status_filter=status_filter,
            min_score=min_score,
        )

    def search_confirmed(self, query):
        return search_confirmed_memory(query)

    def search_candidates(self, query):
        return search_candidate_memory(query)

    def query(self, query, top_n=5, confirmed_only=True):
        return query_memory_index(
            query,
            top_n=top_n,
            confirmed_only=confirmed_only,
        )

    def stats(self, top_n=5):
        return build_repository_statistics(top_n=top_n)

    def health(self):
        return check_memory_health()

    def create_candidate(self, memory):
        return upsert_candidate(memory)

    def get_candidate(self, candidate_id):
        return find_candidate(candidate_id)

    def list_candidates(self, status=None):
        return list_candidates(status=status)

    def confirm_candidate(self, candidate_id):
        return mark_candidate_confirmed(candidate_id)

    def reject_candidate(self, candidate_id, reason=""):
        return mark_candidate_rejected(
            candidate_id,
            reason=reason,
        )

    def candidate_stats(self):
        return candidate_repository_stats()

    def promote(self, memory):
        return promote_memory(memory)


if __name__ == "__main__":
    api = MemoryAPI()

    print("[INFO]")
    print(api.info())

    print("[HEALTH]")
    print(api.health())

    print("[STATS]")
    print(api.stats())

    print("[CANDIDATE_STATS]")
    print(api.candidate_stats())
