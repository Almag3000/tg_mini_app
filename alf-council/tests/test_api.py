import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app, council

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("ALF Council", r.text)

    def test_unknown_symbol(self):
        r = self.client.get("/api/council/DOGEUSDT")
        self.assertEqual(r.status_code, 400)

    def test_council_holds(self):
        r = council({"symbol":"BTCUSDT","last":100.0,"change24h":0.01,"turnover24h":1000.0})
        self.assertEqual(r["proposal"]["action"], "HOLD")
        self.assertFalse(r["risk"]["approved"])

    def test_backtest_invalid_candles(self):
        r = self.client.post("/api/backtest", json={"candles":[]})
        self.assertEqual(r.status_code, 400)

    def test_llm_disabled(self):
        with patch("main.debate", new_callable=AsyncMock, side_effect=RuntimeError("LLM disabled")):
            with patch("main.ticker", new_callable=AsyncMock, return_value={"symbol":"BTCUSDT","last":100.0,"change24h":0.0,"turnover24h":0.0}):
                r = self.client.post("/api/debate/BTCUSDT")
        self.assertEqual(r.status_code, 503)

if __name__ == "__main__":
    unittest.main()
