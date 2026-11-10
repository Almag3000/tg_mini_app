# Security and operating boundaries

- **No live orders**: this repository has no Bybit private-key order execution code.
- No account credentials are needed for public market-data endpoints.
- Optional OpenRouter keys must be passed through environment variables; never commit them.
- Do not publish the FastAPI server on the public internet: there is no authentication or rate limiting.
- The optional LLM endpoint may incur charges and is vulnerable to untrusted market/news content; model outputs are advisory and cannot authorize execution.
- SQLite audit is local, not tamper-evident and not suitable as an exchange execution ledger.
- Paper account loss controls are in-memory and do not survive process restarts. They are not production risk controls.
- Historical backtests are illustrative; results cannot establish profitability.
- Never connect exchange keys with withdrawal permissions.
