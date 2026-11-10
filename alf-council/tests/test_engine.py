import unittest
from engine import PaperAccount, backtest

class RiskTests(unittest.TestCase):
    def test_invalid_stop(self):
        a = PaperAccount()
        with self.assertRaises(ValueError):
            a.open("LONG", 100, 101, "BTCUSDT")

    def test_trade_fee_and_loss(self):
        a = PaperAccount()
        a.open("LONG", 100, 99.5, "BTCUSDT")
        trade = a.close(99.5, "stop")
        self.assertLess(trade["net_pnl"], 0)
        self.assertLess(a.cash, 1000)

    def test_halt(self):
        a = PaperAccount(halted=True)
        with self.assertRaises(ValueError):
            a.open("LONG", 100, 99, "BTCUSDT")

    def test_roundtrip_fee_accounting(self):
        a = PaperAccount()
        a.open("LONG", 100, 99, "BTCUSDT")
        trade = a.close(100)
        self.assertAlmostEqual(trade["net_pnl"], a.cash - a.starting_cash, places=8)
        self.assertAlmostEqual(a.realized_pnl, trade["net_pnl"], places=8)

    def test_daily_loss_halt(self):
        a = PaperAccount()
        a._check_limits("2026-11-10T10:00:00+00:00")
        a.cash = 989.0
        with self.assertRaisesRegex(ValueError, "Daily loss"):
            a.open("LONG", 100, 99, "BTCUSDT", "2026-11-10T10:10:00+00:00")
        self.assertTrue(a.halted)

    def test_backtest(self):
        bars = [{"open": 100+i, "high": 101+i, "low": 99+i, "close": 100+i} for i in range(8)]
        r = backtest(bars)
        self.assertIn("net_pnl", r)
        self.assertGreaterEqual(r["count"], 1)

if __name__ == "__main__":
    unittest.main()
