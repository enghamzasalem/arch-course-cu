# Assignment Submission: Lecture 7

**Student Name**: Amaan Shaikh

## Overview

This submission contains the architecture design for a **Document Processing Pipeline** as a composable system. The design applies concepts from Chapter 7: Composability and Connectors, including component decomposition, connector types, orchestration vs choreography, and API design for both synchronous and asynchronous processing.

## Files Included

### Part 1 – Component and Connector Design

- `part1_components_and_connectors.md` — Component decomposition with 5 components (Validator, Extractor, Classifier, Storage, Notifier) and connector definitions
- `part1_component_connector_diagram.drawio` — Component and connector diagram (draw.io diagram)
- `part1_component_connector_diagram.png` — Component and connector diagram (image)

### Part 2 – Orchestration vs Choreography

- `part2_orchestration.md` — Orchestrated design with orchestrator sequence, error handling, advantages and disadvantages
- `part2_choreography.md` — Event-driven choreography design with events, subscriptions, advantages and disadvantages
- `part2_comparison.md` — Comparison table and recommendation for hybrid approach

### Part 3 – API and Sequence Diagrams

- `part3_api_design.md` — API design for sync and async endpoints (POST /run, POST /jobs, GET /jobs/{id}, webhook callback)
- `part3_sequence_diagram.drawio` — Sequence diagram for synchronous flow (draw.io diagram)
- `part3_sequence_diagram.png` — Sequence diagram for synchronous flow (image)
- `part3_sequence_diagram_async.drawio` — Sequence diagram for asynchronous flow (draw.io diagram)
- `part3_sequence_diagram_async.png` — Sequence diagram for asynchronous flow (image)

### Documentation

- `README.md` — This file

## Key Highlights

- **5 components** with single responsibilities: Validator, Extractor, Classifier, Storage, Notifier
- **Connector types:** REST, direct call, message queue, webhook
- **Sync vs async justification:** Validation/Classification/Storage use sync; Extraction/Notification use async
- **Orchestration:** Pipeline API as central coordinator with error handling and retries
- **Choreography:** Event-driven flow with events (DocumentReceived, ValidationComplete, ExtractionComplete, ClassificationComplete, DocumentStored, NotificationSent)
- **Hybrid recommendation:** Orchestration for sync path, choreography for async path
- **API design:** Separate endpoints for sync and async processing with job status polling and webhook callbacks
- **Sequence diagrams:** Both sync and async flows with 8+ participants each

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files in any text editor or Markdown viewer

## Pipeline Steps

Client → API Gateway → Validator → Extractor → Classifier → Storage → Notifier → Client


## Connector Summary

| From | To | Type | Sync/Async |
|------|-----|------|------------|
| Client | API Gateway | REST | Sync |
| Client | Queue | HTTP POST | Async |
| API Gateway | Validator | Direct Call | Sync |
| Queue | Validator | Message Queue | Async |
| Validator | Extractor | Direct Call | Sync |
| Extractor | Classifier | Direct Call | Sync |
| Classifier | Storage | Direct Call | Sync |
| Storage | Notifier | Direct Call | Async |
| Notifier | Client | Webhook | Async |

## Design Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Sync flow | Orchestration | Client expects immediate result, easier to debug |
| Async flow | Choreography | Background processing works better with events |
| Extraction | Async | OCR can be slow, should not block |
| Notification | Async | Should not affect core processing |
| Callback | Webhook | Client chooses to receive async notifications |