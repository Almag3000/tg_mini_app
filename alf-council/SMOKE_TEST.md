# Release smoke-test checklist

CI is expected to run Python compilation, unittest discovery and Docker build on every change under alf-council. Passing CI is necessary, not sufficient.

## Local
```bash
cd alf-council
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
docker compose up --build -d
curl -fsS http://127.0.0.1:8000/
curl -fsS http://127.0.0.1:8000/api/history/BTCUSDT
curl -fsS http://127.0.0.1:8000/api/evaluate/BTCUSDT
curl -fsS http://127.0.0.1:8000/api/decisions
docker compose down
```
These last four commands require network access to Bybit for the market-data endpoints. No account keys are required.

## Manual acceptance
- Dashboard shows BTCUSDT and ETHUSDT choices.
- Deterministic council returns HOLD and execution disabled.
- LLM debate without keys returns HTTP 503 (no invented output).
- Historical evaluation identifies itself as baseline, NOT LLM council.
- Audit records decisions after calling /api/council/BTCUSDT.
- Server binds to loopback only through compose.
- No live order submission routes or exchange private keys exist.

## Not completed by this checklist
Bybit Demo reconciliation, realistic funding, persistence of paper positions, API authentication, full multi-agent historical replay, walk-forward statistical validation, security review and production hosting.
