import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app

class HistoricalApiTests(unittest.TestCase):
    def setUp(self): self.client = TestClient(app)

    def test_historical_baseline(self):
        bars = [{"timestamp": i, "open": 100+i, "high": 101+i,
                 "low": 99+i, "close": 100+i} for i in range(8)]
        with patch("main.historical_candles", new_callable=AsyncMock, return_value=bars):
            response = self.client.get("/api/backtest/BTCUSDT")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["bars"], 8)
        self.assertIn("NOT LLM", response.json()["strategy"])

    def test_invalid_symbol(self):
        response = self.client.get("/api/history/INVALID")
        self.assertEqual(response.status_code, 400)
