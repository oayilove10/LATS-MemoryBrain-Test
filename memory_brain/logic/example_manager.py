# LATS V3
# Example Manager V1


MAX_EXAMPLES = 10


def add_example(
    memory,
    example_id
):

    examples = memory.get(
        "examples",
        []
    )

    if example_id not in examples:

        examples.append(
            example_id
        )

    if len(examples) > MAX_EXAMPLES:

        examples = examples[
            -MAX_EXAMPLES:
        ]

    memory["examples"] = (
        examples
    )

    memory["example_count"] = (
        len(examples)
    )

    return memory


if __name__ == "__main__":

    memory = {

        "memory_id":
        "MEM001"
    }

    for i in range(12):

        memory = add_example(
            memory,
            f"CHAIN_{i:03d}"
        )

    print(memory)
