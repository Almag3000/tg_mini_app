import os
import tempfile
import unittest
from unittest.mock import patch
from storage import save_decision, recent_decisions

class StorageTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.dict(os.environ, {"ALF_DB_PATH": os.path.join(d, "audit.db")}):
                report = {"market":{"symbol":"BTCUSDT"},"proposal":{"action":"HOLD"}}
                i = save_decision(report)
                rows = recent_decisions()
                self.assertEqual(rows[0]["id"], i)
                self.assertEqual(rows[0]["report"], report)

    def test_limit(self):
        with self.assertRaises(ValueError):
            recent_decisions(101)
