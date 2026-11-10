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
    return """<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ALF Council</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{font:15px system-ui;background:#0b1020;color:#e5e7eb;max-width:1050px;margin:auto;padding:20px}
h1{font-size:32px;margin-bottom:4px}h2{font-size:19px}p,small{color:#a7b0c0}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0}button,select{background:#263451;color:#fff;border:1px solid #445577;border-radius:9px;padding:11px;cursor:pointer}
button:hover{background:#344c77}section{background:#151e32;border:1px solid #2b3954;border-radius:14px;padding:18px;margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
article{background:#1c2942;border-radius:10px;padding:13px;line-height:1.5}
strong{color:#f8fafc}.status{color:#fbbf24}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;max-height:420px;overflow:auto}
</style></head><body>
<h1>ALF Council</h1><p>Исследовательская панель · Публичные данные Bybit · Реальные ордера запрещены</p>
<nav><select id="symbol"><option>BTCUSDT</option><option>ETHUSDT</option></select>
<button onclick="run('council')">Совет (правила)</button>
<button onclick="run('debate')">Дискуссия ИИ</button>
<button onclick="run('evaluate')">Историческая проверка</button>
<button onclick="run('decisions')">Журнал</button></nav>
<section><h2>Состояние</h2><div id="status" class="status">Ожидание запроса. Реальные сделки отключены.</div></section>
<section><h2>Результаты</h2><div id="summary" class="grid"></div><details><summary>Исходные данные JSON</summary><pre id="raw"></pre></details></section>
<small>Дискуссия ИИ требует OpenRouter API key и модели. Историческая проверка — базовая стратегия, не тест совета ИИ. Панель без аутентификации: запускать только локально.</small>
<script>
function card(title,body){let a=document.createElement('article'),b=document.createElement('strong'),p=document.createElement('p');b.textContent=title;p.textContent=body;a.append(b,p);return a}
async function run(kind){
 const symbol=document.getElementById('symbol').value;
 const status=document.getElementById('status'), summary=document.getElementById('summary'),raw=document.getElementById('raw');
 status.textContent='Запрос выполняется...';summary.replaceChildren();raw.textContent='';
 let path=kind==='council'?'/api/council/'+symbol:kind==='debate'?'/api/debate/'+symbol:kind==='evaluate'?'/api/evaluate/'+symbol:'/api/decisions';
 try{let r=await fetch(path,{method:kind==='debate'?'POST':'GET'});let data=await r.json();if(!r.ok)throw Error(data.detail||'HTTP '+r.status);
 raw.textContent=JSON.stringify(data,null,2);status.textContent='Данные получены. Исполнение ордеров отключено.';
 if(kind==='council'){summary.append(card('Решение',data.proposal.action),card('Риск',data.risk.reason));
 for(const round of data.rounds)for(const report of round.reports)summary.append(card(report.agent,report.message))}
 else if(kind==='debate'){summary.append(card('Предложение',data.proposal),card('Разрешение на исполнение',String(data.execution_approved)));
 for(const o of data.round_2)summary.append(card(o.role,o.action+' — '+o.argument))}
 else if(kind==='evaluate'){let v=data.result.out_of_sample;summary.append(card('Контрольный период',v.bars+' свечей'),card('PnL (USDT)',String(v.net_pnl)),card('Сделок',String(v.trades)),card('Win rate',v.win_rate===null?'нет данных':(v.win_rate*100).toFixed(1)+'%'))}
 else{summary.append(card('Записей',String(data.items.length)));for(const d of data.items)summary.append(card(d.symbol+' '+d.action,d.created_at))}
 }catch(e){status.textContent='Ошибка: '+e.message}
}
</script></body></html>"""


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

from market import candles as historical_candles

@app.get("/api/history/{symbol}")
async def history(symbol: str, interval: str = "15", limit: int = 200):
    try:
        return {"symbol": symbol.upper(), "interval": interval,
                "candles": await historical_candles(symbol.upper(), interval, limit)}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Historical data provider unavailable") from exc

@app.get("/api/backtest/{symbol}")
async def historical_backtest(symbol: str, interval: str = "15", limit: int = 200):
    try:
        bars = await historical_candles(symbol.upper(), interval, limit)
        result = backtest(bars)
        return {"symbol": symbol.upper(), "interval": interval, "bars": len(bars),
                "strategy": "naive momentum baseline (NOT LLM council)", "result": result}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Historical data provider unavailable") from exc


from evaluation import evaluate

@app.get("/api/evaluate/{symbol}")
async def historical_evaluation(symbol: str, interval: str = "15", limit: int = 200,
                                train_fraction: float = 0.7):
    try:
        bars = await historical_candles(symbol.upper(), interval, limit)
        result = evaluate(bars, train_fraction)
        return {"symbol": symbol.upper(), "interval": interval, "result": result}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Historical data provider unavailable") from exc
