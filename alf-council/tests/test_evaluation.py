import unittest
from evaluation import evaluate

def bars(n=60):
    return [{"timestamp": i*900000, "open":100+i*.1, "high":101+i*.1,
             "low":99+i*.1, "close":100+i*.1} for i in range(n)]

class EvaluationTests(unittest.TestCase):
    def test_split(self):
        r = evaluate(bars())
        self.assertEqual(r["in_sample"]["bars"], 42)
        self.assertEqual(r["out_of_sample"]["bars"], 18)
        self.assertIn("net_pnl", r["out_of_sample"])

    def test_reject_duplicate(self):
        data = bars()
        data[3]["timestamp"] = data[2]["timestamp"]
        with self.assertRaises(ValueError):
            evaluate(data)

    def test_reject_short(self):
        with self.assertRaises(ValueError):
            evaluate(bars(10))

    def test_reject_fraction(self):
        with self.assertRaises(ValueError):
            evaluate(bars(), .95)
