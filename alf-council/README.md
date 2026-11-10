# ALF Council — experimental MVP

Isolated directory in an existing GitHub repository. **No live trading, no private Bybit API keys, no live order submission.**

## Run
```bash
cd alf-council
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```
Windows: `.venv\\Scripts\\activate`.

Open http://127.0.0.1:8000/ for the dashboard. `GET /api/council/BTCUSDT` retrieves public Bybit ticker data and displays rule-based role reports. Failure to fetch data produces HTTP 503 rather than a synthetic quote.

## Optional LLM discussion
Set `OPENROUTER_API_KEY` and `ALF_LLM_MODEL` in the process environment (never commit secrets). Then `POST /api/debate/BTCUSDT` invokes six model roles over two rounds, using a fixed market snapshot. Model replies are untrusted; the output is **never** routed to an order API. This endpoint may incur provider charges.

## Baseline paper backtest
`POST /api/backtest` with JSON `{"starting_cash":1000,"candles":[{"open":100,"high":102,"low":99,"close":101}, ...]}` (at least 4 valid OHLC bars). This is a **simplified momentum baseline**, not a backtest of the LLM council. It assumes next-bar open fills, fixed fee and slippage, and conservative stop handling; it does not simulate funding, liquidations, latency, market impact or partial fills. Do not interpret results as a live-trading forecast.

## Tests
```bash
cd alf-council
python -m unittest discover -s tests -v
```

## Production blockers
Historical dataset ingestion, full exchange event replay, persistence, independent risk kill switch, Bybit Demo execution and reconciliation, authorization, secrets management, CI, deployment, proper risk accounting across sessions, and statistically sound out-of-sample evaluation are **not implemented**. The paper engine is an isolated library and is not wired to real exchange execution.
