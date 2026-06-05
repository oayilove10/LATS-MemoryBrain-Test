RAW DATABASE

↓

Market Brain

Input:
- 1W
- 1D
- 4H
- 1H

Output:
market_context.json

↓

Trading Brain

Input:
- signal_15m
- market_context.json

Output:
trade_decision.json

↓

AI Chief

Input:
- market_context.json
- trade_decision.json

Output:
final_decision.json

↓

FINAL DECISION
