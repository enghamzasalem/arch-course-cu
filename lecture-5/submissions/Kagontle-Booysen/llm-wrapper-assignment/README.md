# Assignment Submission: Lecture 5

**Student Name**: Kagontle Booysen
**Student ID**: 30009255
**Submission Date**: 03/11/2026

---

## Overview

This submission presents the complete architectural design of an LLM API Wrapper
system that acts as a transparent proxy between internal applications and commercial
LLM providers (OpenAI, Google Gemini). The system adds three layers of value:

  - Track    : Every request/response is recorded (who, when, model, tokens, cost)
  - Monitor  : Metrics and health are exposed (throughput, latency, error rate)
  - Detect   : Unusual patterns are flagged in real time and routed to alerting systems

The work spans four parts: system context (C4 L1), container design (C4 L2),
component decomposition (C4 L3), sequence diagrams, anomaly detection specification,
quality attribute analysis, a working Python proxy, and an ADR.

---

## Files Included

### Part 1 - Context & Containers
  part1_context_diagram.drawio         C4 Level 1 - System Context diagram (editable)
  part1_context_diagram.png            C4 Level 1 - exported image
  part1_container_diagram.drawio       C4 Level 2 - Container diagram (editable)
  part1_container_diagram.png          C4 Level 2 - exported image
  part1_container_descriptions.md      Description and responsibility of each container

### Part 2 - Component Design & Data Flow
  part2_component_diagram.drawio       C4 Level 3 - Anomaly Detection component diagram
  part2_component_diagram.png          C4 Level 3 - exported image
  part2_component_rationale.md         Component responsibilities, interfaces, and rationale
  part2_sequence_request.drawio        Sequence Diagram 1 - Happy path (prompt to completion)
  part2_sequence_request.png           Sequence Diagram 1 - exported image
  part2_sequence_anomaly.drawio        Sequence Diagram 2 - Anomaly detection and alerting flow
  part2_sequence_anomaly.png           Sequence Diagram 2 - exported image

### Part 3 - Anomaly Detection & Quality Attributes
  part3_anomaly_detection.md           5 anomaly types with inputs, detection methods, outputs
  part3_quality_attributes.md          5 quality attributes with trade-offs and scalability note

### Part 4 - Optional (Extra Credit)
  code/proxy.py                        Working Python proxy - forwards to OpenAI or mock
  code/test_proxy.py                   20-test unit suite (all passing)
  code/part4_adr.md                    ADR-001: Where to run anomaly detection
  code/README.md                       Setup instructions and architecture mapping

---

## Key Highlights

1. Full C4 hierarchy (Context -> Container -> Component) with clear traceability
   across all three levels of diagram.

2. Five anomaly types fully specified with detection formulas:
     - Request Rate Spike    : z-score on 5-min rolling window
     - Latency Degradation   : dual-trigger (absolute ceiling + relative multiplier)
     - Error Rate Surge      : SLA threshold with error-type stratification
     - Token / Cost Drift    : per-caller budget ceiling + token drift multiplier
     - Unusual Caller        : per-caller z-score with time-of-day normalisation

3. Zero-latency tracking via fire-and-forget Kafka publish. The Gateway returns
   completions to callers before any tracking or anomaly detection work begins.

4. Working Python proxy with 20/20 tests passing. Logs every request to stdout
   and to logs/requests.jsonl (request_id, tokens, cost_usd, latency_ms, status).

---

## How to View

1. Open .drawio files in draw.io (app.diagrams.net) to see editable diagrams
2. View .png files for quick reference without any tools
3. Read .md files in any Markdown viewer (VS Code, GitHub) or with:
     pandoc file.md -o file.html
4. Run the proxy (no API key needed):
     pip install httpx pytest
     python code/proxy.py --provider mock --prompt "Hello"
     python -m pytest code/test_proxy.py -v
5. Optional HTTP server mode:
     python code/proxy.py --serve --port 8000
     curl -X POST http://localhost:8000/v1/chat \
       -H "Content-Type: application/json" \
       -d '{"prompt": "Hello", "provider": "mock"}'
