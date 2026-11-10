import os
import unittest
from unittest.mock import patch
from llm_agents import ask

class ParsingTests(unittest.IsolatedAsyncioTestCase):
    async def test_markdown_fenced_json(self):
        class Response:
            def raise_for_status(self): pass
            def json(self):
                return {"choices":[{"message":{"content":'\x60\x60\x60json\n{"role":"forged","action":"HOLD","argument":"insufficient","objection":"unknown","confidence":0.2}\n\x60\x60\x60'}}]}
        class Client:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def post(self, *args, **kwargs): return Response()
        with patch.dict(os.environ, {"OPENROUTER_API_KEY":"test","ALF_LLM_MODEL":"test"}):
            with patch("llm_agents.httpx.AsyncClient", return_value=Client()):
                result = await ask("technical", {"last":100})
        self.assertEqual(result.role, "technical")
        self.assertEqual(result.action, "HOLD")
