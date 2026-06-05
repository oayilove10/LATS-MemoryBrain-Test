# LATS V3
# Memory Raw Data Validator V1


def check_raw_data(memory_record):
    """
    V1 mock validator.
    Future: search real raw event/chain/result data.
    """

    if (
        memory_record.get("symbol") in ["BTCUSDT", "ETHUSDT"]
        and memory_record.get("trend") == "up"
        and memory_record.get("cycle") == "continue_up"
    ):
        return {
            "found": True,
            "source": "raw_data",
            "evidence_id": "RAW_CHAIN_SAMPLE_001",
            "similarity": 90,
        }

    return {
        "found": False,
        "source": "raw_data",
        "evidence_id": "",
        "similarity": 0,
    }


if __name__ == "__main__":
    memory_record = {
        "symbol": "ETHUSDT",
        "trend": "up",
        "cycle": "continue_up",
    }

    print(check_raw_data(memory_record))
