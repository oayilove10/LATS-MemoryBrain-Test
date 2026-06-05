# LATS V3
# Memory Promoter V2
#
# Candidate -> Confirm Workflow


def promote_memory(
    new_memory,
    matched_memory=None,
    candidate_memory=None,
    confirm_threshold=2,
):

    # เจอ Memory เดิม
    if matched_memory:

        new_memory["status"] = "confirmed"

        new_memory["confirmed_from"] = (
            matched_memory.get(
                "memory_id",
                ""
            )
        )

        new_memory["promotion_reason"] = (
            "matched_repository"
        )

        return new_memory

    # เจอ Candidate เดิม
    if candidate_memory:

        current_count = int(
            candidate_memory.get(
                "candidate_count",
                1
            )
        )

        current_count += 1

        new_memory["candidate_count"] = (
            current_count
        )

        if current_count >= confirm_threshold:

            new_memory["status"] = (
                "confirmed"
            )

            new_memory["promotion_reason"] = (
                "candidate_confirmed"
            )

            new_memory["confirmed_from"] = (
                candidate_memory.get(
                    "memory_id",
                    ""
                )
            )

        else:

            new_memory["status"] = (
                "waiting_confirm"
            )

            new_memory["promotion_reason"] = (
                "candidate_waiting"
            )

        return new_memory

    # ครั้งแรก
    new_memory["status"] = (
        "waiting_confirm"
    )

    new_memory["candidate_count"] = 1

    new_memory["promotion_reason"] = (
        "first_occurrence"
    )

    return new_memory


if __name__ == "__main__":

    memory = {
        "memory_id": "MEM_NEW"
    }

    print(
        promote_memory(
            memory
        )
    )
