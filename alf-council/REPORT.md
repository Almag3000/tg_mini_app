# ALF Council — implementation and verification report
Date: 2026-11-10

## Implemented
- Public Bybit V5 ticker fetch for BTCUSDT/ETHUSDT, with error handling.
- Six deterministic specialist reports and an arbiter, default HOLD and execution blocked.
- Optional OpenRouter LLM debate: six roles, two sequential rounds, unanimous action otherwise HOLD. This is experimental and cannot place orders.
- Isolated paper-position library with fixed fees/slippage and a simplistic baseline OHLC backtest.
- SQLite decision audit for deterministic council reports; GET /api/decisions.
- FastAPI browser interface, Dockerfile, docker-compose.yml bound to localhost.
- Unit and API tests, GitHub Actions workflow for compile, tests and Docker build.

## Verification
- Repository writes: confirmed via GitHub connector commit SHA.
- CI: workflow committed; **no completed run observed at report creation**.
- Local test execution: **not performed**. The execution container could not resolve github.com to clone the repository.
- Bybit network/API: **not live-tested**.
- LLM provider: **not live-tested** (requires credentials and paid model).
- Docker build: **not verified**.
- Live exchange orders: deliberately not implemented.

## Known limitations and blockers
- Risk thresholds for daily/weekly losses are declared but not enforced by the paper account.
- Paper position engine is not wired to the API, and lacks exchange-order reconciliation, funding, liquidations and realistic slippage.
- OHLC baseline is not an LLM-council backtest. It lacks out-of-sample validation.
- Audit database records deterministic council reports only; LLM debate records are not persisted.
- No API authentication; do not expose this server publicly.
- No secure production secret management, monitoring or deployment.
- No evidence of profitability. Live trading is disabled.

## Acceptance gates before any live trading
1. CI and local test suite pass; reproducible Docker build.
2. Validated historical replay and out-of-sample evaluation with exchange fees/funding.
3. Robust independent risk engine, order reconciliation and fail-safe kill switch.
4. Bybit Demo end-to-end validation and manual approval.
5. Security audit, jurisdiction checks, access control and key permissions.

**Status: experimental prototype, NOT production ready.**

## Follow-up 2026-11-10
- Added loss-gate checks in paper account, corrected entry-fee inclusion in realized round-trip PnL, added two regression tests.
- The pre-existing local ZIP prototype at /mnt/data/alf-council was tested separately: pytest reported 2 passed. **These tests do not validate the updated GitHub branch**, which is a different code tree.
- GitHub workflow runs queried through the connector for the latest earlier commit returned an empty list. No CI success can be claimed.
- No Docker executable available in the local environment; no container build claim.
- The system is still not complete or production-ready. No Bybit Demo or live execution implemented.
