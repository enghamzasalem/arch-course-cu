"""
LLM API Wrapper – Minimal Proxy
================================
Accepts an LLM request, forwards to OpenAI or a Gemini mock,
logs request / response / latency to stdout and to logs/requests.jsonl.

Usage
-----
    # Real OpenAI (requires OPENAI_API_KEY env var)
    python proxy.py --provider openai --prompt "What is 2+2?"

    # Mock provider (no API key needed – always works)
    python proxy.py --provider mock --prompt "Tell me a joke"

    # Start as HTTP server (port 8000)
    python proxy.py --serve
"""

import argparse
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# ── Logging setup ────────────────────────────────────────────────────────────

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
AUDIT_LOG_PATH = LOG_DIR / "requests.jsonl"

# Human-readable console logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("llm-proxy")


# ── Audit logger (one JSON line per request) ──────────────────────────────────

def write_audit_record(record: dict[str, Any]) -> None:
    """Append one structured JSON record to the audit log file."""
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ── Provider implementations ──────────────────────────────────────────────────

def call_openai(prompt: str, model: str, api_key: str) -> dict[str, Any]:
    """Forward the prompt to the real OpenAI chat completions endpoint."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    response.raise_for_status()
    return response.json()


def call_mock(prompt: str, model: str) -> dict[str, Any]:
    """
    Return a deterministic mock response — no API key required.
    Mirrors the OpenAI response schema so downstream parsing is identical.
    """
    # Simulate ~200 ms of inference time
    time.sleep(0.2)
    mock_text = (
        f"[MOCK RESPONSE] You asked: '{prompt}'. "
        "This is a simulated completion from the mock provider. "
        "In production this would be replaced by a real LLM response."
    )
    prompt_tokens = len(prompt.split())
    completion_tokens = len(mock_text.split())
    return {
        "id": f"mock-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": mock_text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


# ── Cost estimation ───────────────────────────────────────────────────────────

# Prices in USD per 1 000 tokens (approximate, March 2025)
PRICE_TABLE: dict[str, dict[str, float]] = {
    "gpt-4o":            {"prompt": 0.005,  "completion": 0.015},
    "gpt-4o-mini":       {"prompt": 0.00015,"completion": 0.0006},
    "gpt-3.5-turbo":     {"prompt": 0.0005, "completion": 0.0015},
    "mock-model":        {"prompt": 0.0,    "completion": 0.0},
}
DEFAULT_PRICE = {"prompt": 0.005, "completion": 0.015}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    prices = PRICE_TABLE.get(model, DEFAULT_PRICE)
    return (
        prompt_tokens    / 1000 * prices["prompt"] +
        completion_tokens / 1000 * prices["completion"]
    )


# ── Core proxy function ───────────────────────────────────────────────────────

def proxy_request(
    prompt: str,
    model: str = "gpt-4o-mini",
    provider: str = "mock",
    caller_id: str = "cli",
) -> dict[str, Any]:
    """
    Main proxy entry point.

    1. Validates inputs.
    2. Forwards to the appropriate provider.
    3. Measures latency.
    4. Computes cost.
    5. Logs to stdout and to the audit file.
    6. Returns a normalised response dict.
    """
    request_id = str(uuid.uuid4())
    t_start = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()

    log.info("→ REQUEST  id=%s provider=%s model=%s caller=%s tokens_estimate=%d",
             request_id, provider, model, caller_id, len(prompt.split()))

    # ── Forward to provider ───────────────────────────────────────────────────
    status = "success"
    error_message = None
    raw_response: dict[str, Any] = {}

    try:
        if provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
            raw_response = call_openai(prompt, model, api_key)

        elif provider == "mock":
            raw_response = call_mock(prompt, model)

        else:
            raise ValueError(f"Unknown provider '{provider}'. Choose 'openai' or 'mock'.")

    except httpx.HTTPStatusError as exc:
        status = "provider_error"
        error_message = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        log.error("Provider error: %s", error_message)

    except Exception as exc:  # noqa: BLE001
        status = "error"
        error_message = str(exc)
        log.error("Proxy error: %s", error_message)

    # ── Measure latency ───────────────────────────────────────────────────────
    latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

    # ── Extract usage ─────────────────────────────────────────────────────────
    usage = raw_response.get("usage", {})
    prompt_tokens     = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens      = usage.get("total_tokens", prompt_tokens + completion_tokens)
    cost_usd          = estimate_cost(model, prompt_tokens, completion_tokens)

    # ── Extract completion text ───────────────────────────────────────────────
    completion_text = ""
    if raw_response.get("choices"):
        completion_text = raw_response["choices"][0].get("message", {}).get("content", "")

    # ── Build audit record ────────────────────────────────────────────────────
    audit_record = {
        "request_id":        request_id,
        "timestamp":         timestamp,
        "caller_id":         caller_id,
        "provider":          provider,
        "model":             model,
        "status":            status,
        "error":             error_message,
        "prompt_tokens":     prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens":      total_tokens,
        "cost_usd":          round(cost_usd, 6),
        "latency_ms":        latency_ms,
    }

    # ── Log to stdout ─────────────────────────────────────────────────────────
    if status == "success":
        log.info(
            "← RESPONSE id=%s status=%s latency=%.1fms tokens=%d cost=$%.6f",
            request_id, status, latency_ms, total_tokens, cost_usd,
        )
        log.info("  completion: %s", completion_text[:200])
    else:
        log.error(
            "← RESPONSE id=%s status=%s latency=%.1fms error=%s",
            request_id, status, latency_ms, error_message,
        )

    # ── Write audit record to file ────────────────────────────────────────────
    write_audit_record(audit_record)
    log.info("  audit log → %s", AUDIT_LOG_PATH)

    # ── Return normalised response ────────────────────────────────────────────
    return {
        "request_id":   request_id,
        "status":       status,
        "completion":   completion_text,
        "usage":        audit_record,
        "raw_response": raw_response,
    }


# ── Minimal HTTP server (optional) ───────────────────────────────────────────

def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Minimal HTTP server using only the standard library (http.server).
    POST /v1/chat   → proxy a request
    GET  /health    → liveness check
    GET  /logs      → last 20 audit records
    """
    import http.server

    class ProxyHandler(http.server.BaseHTTPRequestHandler):

        def log_message(self, fmt, *args):  # suppress default access log
            pass

        def send_json(self, code: int, body: Any) -> None:
            data = json.dumps(body, indent=2).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

            elif self.path == "/logs":
                records = []
                if AUDIT_LOG_PATH.exists():
                    lines = AUDIT_LOG_PATH.read_text().strip().splitlines()
                    for line in lines[-20:]:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                self.send_json(200, {"count": len(records), "records": records})

            else:
                self.send_json(404, {"error": "Not found"})

        def do_POST(self):
            if self.path == "/v1/chat":
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError:
                    self.send_json(400, {"error": "Invalid JSON body"})
                    return

                prompt    = body.get("prompt", "")
                model     = body.get("model", "mock-model")
                provider  = body.get("provider", "mock")
                caller_id = body.get("caller_id", "http-client")

                if not prompt:
                    self.send_json(400, {"error": "'prompt' field is required"})
                    return

                result = proxy_request(prompt, model, provider, caller_id)
                code = 200 if result["status"] == "success" else 502
                self.send_json(code, result)
            else:
                self.send_json(404, {"error": "Not found"})

    server = http.server.HTTPServer((host, port), ProxyHandler)
    log.info("LLM Proxy server listening on http://%s:%d", host, port)
    log.info("  POST /v1/chat  – proxy a request")
    log.info("  GET  /health   – liveness check")
    log.info("  GET  /logs     – last 20 audit records")
    server.serve_forever()


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LLM API Wrapper – Minimal Proxy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--prompt",    default="What is the capital of France?",
                        help="Prompt text to send (default: a simple geography question)")
    parser.add_argument("--model",     default="mock-model",
                        help="Model name (default: mock-model)")
    parser.add_argument("--provider",  default="mock", choices=["openai", "mock"],
                        help="LLM provider to use (default: mock)")
    parser.add_argument("--caller-id", default="cli",
                        help="Caller identifier for audit log (default: cli)")
    parser.add_argument("--serve",     action="store_true",
                        help="Start as HTTP server instead of running one request")
    parser.add_argument("--port",      type=int, default=8000,
                        help="Port for HTTP server mode (default: 8000)")

    args = parser.parse_args()

    if args.serve:
        run_server(port=args.port)
    else:
        result = proxy_request(
            prompt=args.prompt,
            model=args.model,
            provider=args.provider,
            caller_id=args.caller_id,
        )
        print("\n─── Normalised Result ───────────────────────────────────")
        print(json.dumps({k: v for k, v in result.items() if k != "raw_response"}, indent=2))


if __name__ == "__main__":
    main()
