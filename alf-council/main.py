from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from html import escape
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="ALF Council", version="0.1.0")
SYMBOLS = {"BTCUSDT", "ETHUSDT"}
BYBIT = "https://api.bybit.com/v5/market/tickers"

class Proposal(BaseModel):
    symbol: str
    action: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]
    objections: list[str]
    timestamp: str

async def ticker(symbol: str) -> dict:
    if symbol not in SYMBOLS:
        raise HTTPException(400, "Unsupported symbol")
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(BYBIT, params={"category": "linear", "symbol": symbol})
            response.raise_for_status()
            data = response.json()
        if data.get("retCode") != 0 or not data.get("result", {}).get("list"):
            raise ValueError("Bybit returned no ticker")
        t = data["result"]["list"][0]
        return {"symbol": symbol, "last": float(t["lastPrice"]),
                "change24h": float(t["price24hPcnt"]),
                "turnover24h": float(t["turnover24h"])}
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(503, f"Market data unavailable: {exc}") from exc

def council(t: dict) -> dict:
    change = t["change24h"]
    roles = [
        ("Technical", f"24h price change: {change:.2%}. This alone cannot establish a trend."),
        ("Order Flow", "Order book and trades are not ingested: insufficient evidence."),
        ("News", "No verified news feed: cannot assess event risk."),
        ("Strategy", "No tested entry/exit edge: recommend HOLD."),
        ("Skeptic", "A single ticker snapshot is insufficient for trading."),
        ("Macro", "No cross-market context available."),
        ("Arbiter", "HOLD until independent signals and risk constraints are validated."),
    ]
    return {"market": t, "rounds": [
        {"round": 1, "reports": [{"agent": n, "message": m} for n, m in roles[:-1]]},
        {"round": 2, "reports": [{"agent": "Skeptic", "message": "Challenge: insufficient market depth, slippage model and historical validation."}]},
        {"round": 3, "reports": [{"agent": roles[-1][0], "message": roles[-1][1]}]}
    ], "proposal": Proposal(symbol=t["symbol"], action="HOLD", confidence=0.0,
          evidence=["Public ticker fetched"], objections=["No validated strategy"],
          timestamp=datetime.now(timezone.utc).isoformat()).model_dump(),
          "risk": {"approved": False, "reason": "Paper-only MVP; execution disabled"}}

@app.get("/api/council/{symbol}")
async def analyze(symbol: str):
    report = council(await ticker(symbol.upper()))
    from storage import save_decision
    save_decision(report)
    return report

@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!doctype html><html lang="ru"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ALF Council</title><style>body{font:16px system-ui;background:#101521;color:#f1f5f9;max-width:820px;margin:40px auto;padding:16px}
button{padding:12px;border:0;border-radius:8px;cursor:pointer}pre{white-space:pre-wrap;background:#1e293b;padding:18px;border-radius:12px}
small{color:#94a3b8}</style><h1>ALF Council</h1>
<p>Мультиагентный прототип · Только наблюдение · Реальные сделки отключены</p>
<button onclick="load('BTCUSDT')">BTCUSDT</button> <button onclick="load('ETHUSDT')">ETHUSDT</button>
<pre id="out">Выберите инструмент</pre><small>Роли основаны на правилах; LLM пока не подключены.</small>
<script>async function load(s){const o=document.getElementById('out');o.textContent='Загрузка...';
try{let r=await fetch('/api/council/'+s);let j=await r.json();o.textContent=JSON.stringify(j,null,2)}
catch(e){o.textContent=String(e)}}</script></html>"""


from engine import backtest
from llm_agents import debate

class BacktestRequest(BaseModel):
    candles: list[dict]
    starting_cash: float = Field(default=1000, gt=0, le=1000000)

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    try:
        return backtest(request.candles, request.starting_cash)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/api/debate/{symbol}")
async def run_debate(symbol: str):
    market = await ticker(symbol.upper())
    try:
        return await debate(market)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(502, f"LLM provider error: {exc}") from exc

@app.get("/api/decisions")
async def decisions(limit: int = 20):
    from storage import recent_decisions
    try:
        return {"items": recent_decisions(limit)}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
