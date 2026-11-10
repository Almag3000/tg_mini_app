"""Deterministic paper execution and auditable risk checks. No live order API."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite

@dataclass
class Limits:
    risk_fraction: float = .0025
    daily_loss_fraction: float = .01
    weekly_loss_fraction: float = .03
    max_notional_fraction: float = 1.0
    fee_fraction: float = .0006
    slippage_fraction: float = .0002

@dataclass
class PaperAccount:
    cash: float = 1000.0
    starting_cash: float = 1000.0
    realized_pnl: float = 0.0
    trades: list = field(default_factory=list)
    limits: Limits = field(default_factory=Limits)
    halted: bool = False
    # MVP permits one round-trip position at a time.
    position: dict | None = None

    def equity(self, mark: float | None = None) -> float:
        if not self.position:
            return self.cash
        p = self.position
        m = p["entry"] if mark is None else mark
        return self.cash + p["qty"] * (m - p["entry"]) * p["side"]

    def open(self, side: str, price: float, stop: float, symbol: str, timestamp: str | None = None) -> dict:
        if self.halted or self.position:
            raise ValueError("Halted or position already open")
        if side not in ("LONG", "SHORT") or symbol not in ("BTCUSDT", "ETHUSDT"):
            raise ValueError("Invalid side or symbol")
        if not all(isfinite(x) and x > 0 for x in (price, stop, self.cash)):
            raise ValueError("Invalid price, stop or cash")
        if (side == "LONG" and stop >= price) or (side == "SHORT" and stop <= price):
            raise ValueError("Stop must be on the loss side")
        dist = abs(price - stop)
        budget = self.cash * self.limits.risk_fraction
        qty = min(budget / (dist + price * (self.limits.fee_fraction * 2 + self.limits.slippage_fraction * 2)),
                  self.cash * self.limits.max_notional_fraction / price)
        if qty <= 0:
            raise ValueError("No capacity")
        entry = price * (1 + self.limits.slippage_fraction * (1 if side == "LONG" else -1))
        fee = qty * entry * self.limits.fee_fraction
        self.cash -= fee
        self.position = dict(symbol=symbol, side=1 if side == "LONG" else -1, qty=qty,
                             entry=entry, stop=stop, opened=timestamp or datetime.now(timezone.utc).isoformat())
        return dict(self.position)

    def close(self, price: float, reason: str = "manual") -> dict:
        if not self.position or not isfinite(price) or price <= 0:
            raise ValueError("Invalid close")
        p = self.position
        exit_price = price * (1 - self.limits.slippage_fraction * p["side"])
        fee = p["qty"] * exit_price * self.limits.fee_fraction
        pnl = p["qty"] * (exit_price - p["entry"]) * p["side"] - fee
        self.cash += pnl
        self.realized_pnl += pnl
        trade = dict(**p, exit=exit_price, net_pnl=pnl, reason=reason)
        self.trades.append(trade)
        self.position = None
        return trade

    def mark(self, price: float) -> dict | None:
        if not self.position:
            return None
        p = self.position
        if (p["side"] == 1 and price <= p["stop"]) or (p["side"] == -1 and price >= p["stop"]):
            return self.close(price, "stop-triggered")
        return None

def backtest(candles: list[dict], starting_cash: float = 1000) -> dict:
    """Simple close-to-close momentum baseline; next bar open fills; conservative intrabar stops.
    Does not model funding, partial fills, liquidations or exchange outage.
    """
    account = PaperAccount(cash=starting_cash, starting_cash=starting_cash)
    if len(candles) < 4:
        raise ValueError("Need at least four OHLC candles")
    for c in candles:
        if not all(k in c for k in ("open", "high", "low", "close")):
            raise ValueError("Missing OHLC")
        if not (0 < c["low"] <= min(c["open"], c["close"]) <= max(c["open"], c["close"]) <= c["high"]):
            raise ValueError("Invalid OHLC")
    for i in range(2, len(candles)):
        prev, cur = candles[i-1], candles[i]
        if account.position:
            p = account.position
            if p["side"] == 1 and cur["low"] <= p["stop"]:
                account.close(min(cur["open"], p["stop"]), "stop")
            elif p["side"] == -1 and cur["high"] >= p["stop"]:
                account.close(max(cur["open"], p["stop"]), "stop")
            else:
                account.close(cur["open"], "next-bar-exit")
        if i == len(candles)-1:
            continue
        before = candles[i-2]
        side = "LONG" if prev["close"] > before["close"] else "SHORT" if prev["close"] < before["close"] else None
        if side:
            stop = cur["open"] * (.995 if side == "LONG" else 1.005)
            account.open(side, cur["open"], stop, "BTCUSDT")
    return {"ending_cash": round(account.cash, 4), "net_pnl": round(account.cash-starting_cash, 4),
            "trades": account.trades, "count": len(account.trades),
            "limitations": ["Baseline only", "No funding", "No market impact", "No liquidation modeling"]}
