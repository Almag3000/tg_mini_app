"""Public Bybit historical kline ingestion; no account access or orders."""
import httpx

BASE = "https://api.bybit.com/v5/market/kline"
SYMBOLS = {"BTCUSDT", "ETHUSDT"}
INTERVALS = {"1", "3", "5", "15", "30", "60", "120", "240", "D"}
async def candles(symbol: str, interval: str = "15", limit: int = 200) -> list[dict]:
    if symbol not in SYMBOLS or interval not in INTERVALS or not 4 <= limit <= 1000:
        raise ValueError("Unsupported symbol, interval or limit")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(BASE, params={"category": "linear", "symbol": symbol, "interval": interval, "limit": limit})
        response.raise_for_status()
        data = response.json()
    if data.get("retCode") != 0:
        raise ValueError("Bybit rejected candle request")
    raw = data.get("result", {}).get("list", [])
    result = []
    seen = set()
    for row in raw:
        if len(row) < 5:
            raise ValueError("Malformed Bybit candle")
        ts = int(row[0])
        if ts in seen:
            raise ValueError("Duplicate timestamp")
        seen.add(ts)
        bar = {"timestamp": ts, "open": float(row[1]), "high": float(row[2]),
               "low": float(row[3]), "close": float(row[4])}
        if not (0 < bar["low"] <= min(bar["open"], bar["close"]) <= max(bar["open"], bar["close"]) <= bar["high"]):
            raise ValueError("Invalid OHLC from Bybit")
        result.append(bar)
    result.sort(key=lambda x: x["timestamp"])
    # Bybit includes the active unfinished candle. Drop it using interval duration for minute-based intervals.
    if interval.isdigit() and result:
        import time
        if result[-1]["timestamp"] + int(interval) * 60000 > int(time.time() * 1000):
            result.pop()
    if len(result) < 4:
        raise ValueError("Not enough closed candles")
    return result
