import unittest
from unittest.mock import AsyncMock, patch
from market import candles

class MarketTests(unittest.IsolatedAsyncioTestCase):
    async def test_reject_bad_symbol(self):
        with self.assertRaises(ValueError):
            await candles("XRPUSDT")

    async def test_normalize_and_sort(self):
        class Response:
            def raise_for_status(self): pass
            def json(self):
                return {"retCode": 0, "result": {"list": [
                    [str(i*900000), str(100+i), str(101+i), str(99+i), str(100+i)]
                    for i in (5,4,3,2,1)
                ]}}
        class Client:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def get(self, *args, **kwargs): return Response()
        with patch("market.httpx.AsyncClient", return_value=Client()):
            result = await candles("BTCUSDT", "15", 10)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["timestamp"], 900000)
        self.assertEqual(result[-1]["timestamp"], 4500000)
