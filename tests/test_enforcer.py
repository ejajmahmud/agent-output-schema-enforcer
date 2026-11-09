"""Unit tests for agent-output-schema-enforcer."""
import unittest
from agent_output_schema_enforcer.enforcer import OutputSchemaEnforcer


class TestOutputSchemaEnforcer(unittest.TestCase):
    def setUp(self):
        self.enforcer = OutputSchemaEnforcer()

    def test_markdown_fence_stripping(self):
        text = "```json\n{\"a\": 1}\n```"
        res = self.enforcer.enforce_json(text)
        self.assertTrue(res.success)
        self.assertEqual(res.data.get("a"), 1)

    def test_unclosed_brace_repair(self):
        text = '{"status": "ok", "count": 10'
        res = self.enforcer.enforce_json(text)
        self.assertTrue(res.success)
        self.assertTrue(res.was_repaired)
        self.assertEqual(res.data.get("status"), "ok")
