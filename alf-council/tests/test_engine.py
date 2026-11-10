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

    def test_backtest(self):
        bars = [{"open": 100+i, "high": 101+i, "low": 99+i, "close": 100+i} for i in range(8)]
        r = backtest(bars)
        self.assertIn("net_pnl", r)
        self.assertGreaterEqual(r["count"], 1)

if __name__ == "__main__":
    unittest.main()
