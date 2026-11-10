"""Walk-forward evaluation of a non-LLM baseline. Not investment advice."""
from __future__ import annotations
from statistics import mean, pstdev
from math import sqrt, isfinite
from engine import backtest

def evaluate(candles: list[dict], train_fraction: float = .7, initial_cash: float = 1000.0) -> dict:
    if not 0.5 <= train_fraction <= 0.9:
        raise ValueError("train_fraction must be 0.5..0.9")
    if not isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError("Invalid initial cash")
    if len(candles) < 30:
        raise ValueError("At least 30 candles required")
    # Only closed candles in chronological order, no repeated timestamps.
    stamps = [c.get("timestamp") for c in candles]
    if any(not isinstance(t, int) for t in stamps) or any(a >= b for a,b in zip(stamps,stamps[1:])):
        raise ValueError("Candles must have strictly increasing integer timestamps")
    cut = int(len(candles) * train_fraction)
    # 2 preceding bars supply warm-up context; trades are entered from the third bar.
    train = backtest(candles[:cut], initial_cash)
    test = backtest(candles[cut-2:], initial_cash)
    pnl = [t["net_pnl"] for t in test["trades"]]
    wins = sum(p > 0 for p in pnl)
    losses = sum(p < 0 for p in pnl)
    gross_win = sum(p for p in pnl if p > 0)
    gross_loss = -sum(p for p in pnl if p < 0)
    return {
        "strategy": "naive momentum baseline, NOT LLM council",
        "in_sample": {"bars": cut, "net_pnl": train["net_pnl"], "trades": train["count"]},
        "out_of_sample": {"bars": len(candles)-cut, "net_pnl": test["net_pnl"],
            "return_fraction": round(test["net_pnl"]/initial_cash, 8),
            "trades": test["count"], "wins": wins, "losses": losses,
            "win_rate": round(wins/len(pnl), 6) if pnl else None,
            "profit_factor": round(gross_win/gross_loss, 6) if gross_loss else None},
        "warnings": ["Single chronological split only", "No parameter optimization",
                     "No funding, liquidation or market impact", "No statistical significance claim"]
    }
