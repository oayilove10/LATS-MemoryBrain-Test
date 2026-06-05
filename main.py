# ============================================================
# FILE: main.py
# LATS V2
# Main Pipeline Test
# ============================================================

from core.raw_data_loader import load_raw_candle_from_kline
from core.event_builder import build_signal_event, validate_signal_event
from core.result_builder import build_empty_result, validate_result_row
from memory.market_memory import build_or_update_memory
from memory.trading_memory import build_trading_memory, validate_trading_memory


def run_pipeline_test():
    print("====================================")
    print("LATS V2 PIPELINE TEST")
    print("====================================")

    # --------------------------------------------------------
    # 1. SAMPLE RAW KLINE
    # --------------------------------------------------------
    symbol = "BTCUSDT"
    timeframe = "15m"

    sample_kline = [
        1748111400000,   # open_time_ms
        "100",           # open
        "105",           # high
        "98",            # low
        "103",           # close
        "1000",          # volume
        1748112300000,   # close_time_ms
    ]

    raw_row = load_raw_candle_from_kline(
        symbol,
        timeframe,
        sample_kline
    )

    print("\n[1] RAW ROW")
    print(raw_row)

    # --------------------------------------------------------
    # 2. BUILD SIGNAL EVENT
    # --------------------------------------------------------
    signal_event = build_signal_event(raw_row)

    # ใส่ค่าทดลองเพื่อให้ Market Memory มี pattern ชัด
    signal_event["signal_type"] = "LONG"
    signal_event["trend_4h"] = "up"
    signal_event["zone"] = "support"

    print("\n[2] SIGNAL EVENT")
    print(signal_event)

    print("SIGNAL VALID:", validate_signal_event(signal_event))

    # --------------------------------------------------------
    # 3. BUILD EMPTY RESULT
    # --------------------------------------------------------
    result_row = build_empty_result(signal_event)

    # ใส่ผลทดลอง
    result_row["status"] = "done"
    result_row["result_10"] = "win"
    result_row["mfe"] = 2.3
    result_row["mae"] = 0.8

    print("\n[3] RESULT ROW")
    print(result_row)

    print("RESULT VALID:", validate_result_row(result_row))

    # --------------------------------------------------------
    # 4. BUILD MARKET MEMORY
    # --------------------------------------------------------
    memory_store = {}

    memory_store = build_or_update_memory(
        memory_store,
        signal_event,
        result_row
    )

    print("\n[4] MARKET MEMORY")
    print(memory_store)

    # ดึง memory ตัวแรกออกมาใช้ต่อ
    pattern_id = list(memory_store.keys())[0]
    market_memory = memory_store[pattern_id]

    # --------------------------------------------------------
    # 5. BUILD TRADING MEMORY
    # --------------------------------------------------------
    trading_memory = build_trading_memory(market_memory)

    print("\n[5] TRADING MEMORY")
    print(trading_memory)

    print("TRADING VALID:", validate_trading_memory(trading_memory))

    # --------------------------------------------------------
    # 6. FINAL DECISION
    # --------------------------------------------------------
    print("\n[6] FINAL DECISION")
    print("PATTERN:", trading_memory["pattern_name"])
    print("ACTION:", trading_memory["action"])
    print("ENTRY:", trading_memory["entry_timing"])
    print("RISK:", trading_memory["risk_note"])

    print("\n====================================")
    print("PIPELINE TEST DONE")
    print("====================================")


if __name__ == "__main__":
    run_pipeline_test()