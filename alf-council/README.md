# ALF Council MVP

Isolated proof of concept inside an existing repository. **Paper-only: no real order placement and no exchange API keys.**

## Run

```bash
cd alf-council
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/ . Market data is fetched from Bybit public V5 tickers; if unavailable the API returns an error instead of inventing prices. Seven deterministic role reports are generated and a conservative risk gate blocks execution. This is not a trained LLM ensemble or a validated trading strategy.
