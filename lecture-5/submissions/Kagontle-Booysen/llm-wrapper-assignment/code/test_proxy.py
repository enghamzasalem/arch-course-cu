"""
Tests for the LLM API Wrapper proxy.
Run with: python -m pytest test_proxy.py -v
"""

import json
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from proxy import (
    AUDIT_LOG_PATH,
    call_mock,
    estimate_cost,
    proxy_request,
    write_audit_record,
)


class TestCallMock(unittest.TestCase):
    """Unit tests for the mock provider."""

    def test_returns_valid_schema(self):
        result = call_mock("Hello", "mock-model")
        self.assertIn("choices", result)
        self.assertIn("usage", result)
        self.assertEqual(result["choices"][0]["message"]["role"], "assistant")

    def test_completion_contains_prompt(self):
        result = call_mock("What is 2+2?", "mock-model")
        content = result["choices"][0]["message"]["content"]
        self.assertIn("What is 2+2?", content)

    def test_token_counts_are_positive(self):
        result = call_mock("Tell me something", "mock-model")
        self.assertGreater(result["usage"]["prompt_tokens"], 0)
        self.assertGreater(result["usage"]["completion_tokens"], 0)

    def test_simulates_latency(self):
        t0 = time.perf_counter()
        call_mock("Quick test", "mock-model")
        elapsed = time.perf_counter() - t0
        # Mock sleeps 0.2 s; allow generous upper bound for slow CI
        self.assertGreater(elapsed, 0.1)
        self.assertLess(elapsed, 2.0)


class TestEstimateCost(unittest.TestCase):
    """Unit tests for the cost calculation."""

    def test_known_model_cost(self):
        # gpt-4o: $0.005/1k prompt + $0.015/1k completion
        cost = estimate_cost("gpt-4o", prompt_tokens=1000, completion_tokens=1000)
        self.assertAlmostEqual(cost, 0.020, places=5)

    def test_mock_model_zero_cost(self):
        cost = estimate_cost("mock-model", 500, 500)
        self.assertEqual(cost, 0.0)

    def test_unknown_model_uses_default(self):
        cost = estimate_cost("unknown-future-model", 1000, 1000)
        self.assertGreater(cost, 0)

    def test_zero_tokens_zero_cost(self):
        cost = estimate_cost("gpt-4o-mini", 0, 0)
        self.assertEqual(cost, 0.0)


class TestWriteAuditRecord(unittest.TestCase):
    """Unit tests for audit log writing."""

    def setUp(self):
        # Use a temp audit file so tests don't pollute the real log
        self.original_path = AUDIT_LOG_PATH
        import proxy
        self._proxy_module = proxy
        proxy.AUDIT_LOG_PATH = Path("logs/test_audit.jsonl")
        proxy.AUDIT_LOG_PATH.parent.mkdir(exist_ok=True)
        # Clear before each test
        if proxy.AUDIT_LOG_PATH.exists():
            proxy.AUDIT_LOG_PATH.unlink()

    def tearDown(self):
        self._proxy_module.AUDIT_LOG_PATH = self.original_path

    def test_writes_valid_json_line(self):
        record = {"request_id": "abc123", "status": "success", "cost_usd": 0.001}
        write_audit_record(record)
        line = self._proxy_module.AUDIT_LOG_PATH.read_text().strip()
        parsed = json.loads(line)
        self.assertEqual(parsed["request_id"], "abc123")

    def test_appends_multiple_records(self):
        write_audit_record({"id": 1})
        write_audit_record({"id": 2})
        write_audit_record({"id": 3})
        lines = self._proxy_module.AUDIT_LOG_PATH.read_text().strip().splitlines()
        self.assertEqual(len(lines), 3)


class TestProxyRequest(unittest.TestCase):
    """Integration-style tests for the main proxy_request function."""

    def setUp(self):
        import proxy
        self._proxy_module = proxy
        proxy.AUDIT_LOG_PATH = Path("logs/test_proxy_audit.jsonl")
        proxy.AUDIT_LOG_PATH.parent.mkdir(exist_ok=True)
        if proxy.AUDIT_LOG_PATH.exists():
            proxy.AUDIT_LOG_PATH.unlink()

    def tearDown(self):
        self._proxy_module.AUDIT_LOG_PATH = AUDIT_LOG_PATH

    def test_mock_provider_success(self):
        result = proxy_request("What is 2+2?", model="mock-model", provider="mock")
        self.assertEqual(result["status"], "success")
        self.assertIn("completion", result)
        self.assertTrue(len(result["completion"]) > 0)

    def test_result_has_request_id(self):
        result = proxy_request("Hello", provider="mock")
        self.assertIn("request_id", result)
        self.assertTrue(len(result["request_id"]) > 0)

    def test_usage_fields_present(self):
        result = proxy_request("Count to three", provider="mock")
        usage = result["usage"]
        for field in ["prompt_tokens", "completion_tokens", "cost_usd", "latency_ms"]:
            self.assertIn(field, usage)

    def test_latency_is_positive(self):
        result = proxy_request("Quick question", provider="mock")
        self.assertGreater(result["usage"]["latency_ms"], 0)

    def test_audit_record_written(self):
        proxy_request("Test audit logging", provider="mock", caller_id="test-suite")
        self.assertTrue(self._proxy_module.AUDIT_LOG_PATH.exists())
        line = self._proxy_module.AUDIT_LOG_PATH.read_text().strip().splitlines()[-1]
        record = json.loads(line)
        self.assertEqual(record["caller_id"], "test-suite")
        self.assertEqual(record["status"], "success")

    def test_unknown_provider_returns_error(self):
        result = proxy_request("Hello", provider="nonexistent")
        self.assertEqual(result["status"], "error")
        self.assertIsNone(result["completion"] or None)

    def test_multiple_requests_all_logged(self):
        for i in range(3):
            proxy_request(f"Request number {i}", provider="mock")
        lines = self._proxy_module.AUDIT_LOG_PATH.read_text().strip().splitlines()
        self.assertEqual(len(lines), 3)

    def test_openai_missing_key_returns_error(self):
        with patch.dict("os.environ", {}, clear=True):
            # Ensure OPENAI_API_KEY is absent
            import os
            os.environ.pop("OPENAI_API_KEY", None)
            result = proxy_request("Hello", provider="openai")
        self.assertEqual(result["status"], "error")
        self.assertIn("OPENAI_API_KEY", result["usage"]["error"])

    def test_openai_http_error_returns_provider_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"

        import httpx
        with patch("proxy.call_openai") as mock_call, \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            mock_call.side_effect = httpx.HTTPStatusError(
                "429", request=MagicMock(), response=mock_response
            )
            result = proxy_request("Hello", provider="openai")

        self.assertIn(result["status"], ["provider_error", "error"])


class TestCostTable(unittest.TestCase):
    """Verify all known models in the price table produce non-negative costs."""

    def test_all_known_models_non_negative(self):
        from proxy import PRICE_TABLE
        for model in PRICE_TABLE:
            cost = estimate_cost(model, 100, 100)
            self.assertGreaterEqual(cost, 0.0, f"Negative cost for model {model}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
