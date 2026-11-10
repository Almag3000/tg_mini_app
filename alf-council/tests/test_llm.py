import os
import unittest
from unittest.mock import AsyncMock, patch
from llm_agents import ask, debate

class LlmTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_credentials(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "", "ALF_LLM_MODEL": ""}):
            with self.assertRaises(RuntimeError):
                await ask("technical", {"last": 100})

    async def test_unanimous_votes_still_block_execution(self):
        async def fake_ask(role, snapshot, previous=None):
            from llm_agents import Opinion
            return Opinion(role=role, action="LONG", argument="test", objection="test", confidence=.5)
        with patch("llm_agents.ask", side_effect=fake_ask):
            result = await debate({"last": 100})
        self.assertEqual(result["proposal"], "LONG")
        self.assertFalse(result["execution_approved"])
        self.assertEqual(len(result["round_1"]), 6)
        self.assertEqual(len(result["round_2"]), 6)

    async def test_disagreement_holds(self):
        async def fake_ask(role, snapshot, previous=None):
            from llm_agents import Opinion
            return Opinion(role=role, action="SHORT" if role == "skeptic" else "LONG",
                           argument="test", objection="test", confidence=.5)
        with patch("llm_agents.ask", side_effect=fake_ask):
            result = await debate({"last": 100})
        self.assertEqual(result["proposal"], "HOLD")
