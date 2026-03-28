# LLM API Wrapper – Minimal Proxy (Part 4, Option A)

A self-contained Python proxy that accepts an LLM request, forwards it to
OpenAI or a built-in mock provider, and logs every request/response/latency
to stdout and to `logs/requests.jsonl`.

## Files

```
code/
├── proxy.py          # Main proxy (CLI + optional HTTP server)
├── test_proxy.py     # 20-test suite (unittest + pytest)
├── part4_adr.md      # ADR-001: Where to run anomaly detection
└── logs/
    └── requests.jsonl  # Audit log (created on first run)
```

## Requirements

```bash
pip install httpx pytest
```

Only two dependencies. The HTTP server mode uses the Python standard library only.

---

## Usage

### 1. Single request — mock provider (no API key needed)

```bash
python proxy.py --prompt "What is the capital of France?" --provider mock
```

**Output (stdout):**
```
2025-03-12T10:00:01 [INFO] → REQUEST  id=abc123 provider=mock model=mock-model caller=cli
2025-03-12T10:00:01 [INFO] ← RESPONSE id=abc123 status=success latency=200.8ms tokens=42 cost=$0.000000
2025-03-12T10:00:01 [INFO]   completion: [MOCK RESPONSE] You asked: 'What is the capital of France?'...
2025-03-12T10:00:01 [INFO]   audit log → logs/requests.jsonl
```

### 2. Single request — real OpenAI

```bash
export OPENAI_API_KEY=sk-...
python proxy.py --prompt "Explain recursion briefly" --provider openai --model gpt-4o-mini
```

### 3. HTTP server mode

```bash
python proxy.py --serve --port 8000
```

Then in another terminal:

```bash
# Proxy a request
curl -s -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?", "provider": "mock", "caller_id": "curl-test"}' | python3 -m json.tool

# Health check
curl http://localhost:8000/health

# Last 20 audit records
curl http://localhost:8000/logs
```

### 4. Run tests

```bash
python -m pytest test_proxy.py -v
```

Expected: **20 passed**.

---

## What gets logged

Every request writes one JSON line to `logs/requests.jsonl`:

```json
{
  "request_id":        "960072b4-c6df-4a4c-8e5e-f1e968a11feb",
  "timestamp":         "2025-03-12T10:00:01.408998+00:00",
  "caller_id":         "cli",
  "provider":          "mock",
  "model":             "mock-model",
  "status":            "success",
  "error":             null,
  "prompt_tokens":     9,
  "completion_tokens": 33,
  "total_tokens":      42,
  "cost_usd":          0.0,
  "latency_ms":        200.79
}
```

This is exactly the schema written to PostgreSQL in the full architecture
(`Request Log Store`, Task 1.2).

---

## Architecture mapping

| Proxy component | Full architecture equivalent |
|---|---|
| `proxy_request()` | API Gateway / Proxy container |
| `write_audit_record()` | Tracking & Ingestion Service (simplified — writes directly) |
| `estimate_cost()` | Cost computation in Tracking Service |
| `call_openai()` | Gateway → OpenAI API (forwarding) |
| `call_mock()` | Stub for Gemini or any secondary provider |
| `logs/requests.jsonl` | Request Log Store (PostgreSQL) |
| HTTP server `/health` | `/health` endpoint on every container |
| HTTP server `/logs` | Monitoring Service audit query endpoint |
