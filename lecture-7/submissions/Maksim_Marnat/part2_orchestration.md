# Part 2.1 — Orchestrated design

## Orchestrator

**Component:** **Pipeline API** (includes an internal **PipelineOrchestrator** module for the synchronous path; async path hands one command to the worker, which reuses the same ordered steps).

## Call sequence (happy path)

1. API receives request → **Validator** (sync RPC).
2. On success → **Extractor** (sync in-process or sync RPC if separate service within SLA).
3. On success → **Classifier** (sync).
4. On success → **Storage** (sync PUT of artifacts + metadata).
5. On success → enqueue **Notifier** work or call notifier client (async, non-blocking to response assembly).
6. API returns aggregated JSON (sync) or marks job completed (async worker).

## Errors and retries

- **Validator / Classifier failures:** return **4xx** mapping to client; **no** pipeline retry (bad input).
- **Transient extractor/storage errors:** orchestrator (or worker) **retries with backoff**; cap attempts; on exhaustion → job `failed`, optional DLQ.
- **Idempotency:** `job_id` + content hash for storage keys to avoid duplicate artifacts on retry.

## Trade-offs (this pipeline)

- **Advantage:** Single place knows order and policy; easy to enforce timeouts, tracing, and consistent error mapping.
- **Disadvantage:** Orchestrator (API tier) can become a **bottleneck** and must be scaled; adding steps requires changing central flow code.
