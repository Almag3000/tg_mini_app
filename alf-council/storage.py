"""SQLite append-only audit log for council decisions."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

def database_path() -> str:
    return os.environ.get("ALF_DB_PATH", "alf_council.sqlite3")

def connect():
    db = sqlite3.connect(database_path(), timeout=5)
    db.execute("CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, symbol TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL)")
    db.commit()
    return db

def save_decision(report: dict) -> int:
    symbol = report["market"]["symbol"]
    action = report["proposal"]["action"]
    if symbol not in ("BTCUSDT", "ETHUSDT") or action not in ("HOLD", "LONG", "SHORT"):
        raise ValueError("Invalid decision")
    with connect() as db:
        cursor = db.execute("INSERT INTO decisions (created_at,symbol,action,payload) VALUES (?,?,?,?)",
                            (datetime.now(timezone.utc).isoformat(), symbol, action, json.dumps(report, allow_nan=False)))
        db.commit()
        return cursor.lastrowid

def recent_decisions(limit: int = 20) -> list[dict]:
    if not 1 <= limit <= 100:
        raise ValueError("Invalid limit")
    with connect() as db:
        rows = db.execute("SELECT id,created_at,symbol,action,payload FROM decisions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [{"id": r[0], "created_at": r[1], "symbol": r[2], "action": r[3], "report": json.loads(r[4])} for r in rows]
