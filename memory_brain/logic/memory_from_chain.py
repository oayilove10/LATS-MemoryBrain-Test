# LATS V3 V1
# Memory From Chain


def build_memory_record(chain):

    memory_id = (
        "MEM_" +
        chain.get(
            "chain_id",
            "UNKNOWN"
        )
    )

    return {

        "memory_id":
            memory_id,

        "symbol":
            chain.get(
                "symbol",
                ""
            ),

        "chain_id":
            chain.get(
                "chain_id",
                ""
            ),

        "trend":
            chain.get(
                "trend",
                "unknown"
            ),

        "cycle":
            chain.get(
                "cycle",
                "unknown"
            ),

        "result":
            chain.get(
                "result",
                ""
            ),

        "status":
            "candidate",
    }


if __name__ == "__main__":

    chain = {

        "chain_id":
        "CHAIN_BTCUSDT_4H_BULL_CLOSE_15m_LONG_SIGNAL",

        "symbol":
        "BTCUSDT",

        "trend":
        "up",

        "cycle":
        "continue_up",

        "result":
        "",
    }

    print(
        build_memory_record(
            chain
        )
    )
