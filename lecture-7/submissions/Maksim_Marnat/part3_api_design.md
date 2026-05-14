# Part 3 — API design

## Endpoints (REST)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/pipeline/run` | **Sync:** body = URL or multipart file + options (`extract_mode`, `classify: bool`); response = extracted text, classification, storage refs or error. |
| `POST` | `/api/v1/pipeline/jobs` | **Async:** same body + optional `callback_url`; response = `202` + `{ "job_id", "status_url" }`. |
| `GET` | `/api/v1/pipeline/jobs/{job_id}` | Status: `queued \| running \| succeeded \| failed` + result payload when done. |

Optional: `callback_url` invoked by **Notifier** on terminal state (mirrors GET).

## Sync path (components)

Client → **Pipeline API** (orchestrator) → **Validator** (internal sync RPC) → **Extractor** → **Classifier** → **Storage**; response built from in-memory result. **Notifier** skipped or used only for optional audit webhook.

## Async path (components)

Client → **Pipeline API** persists `job_id`, enqueues **PipelineCommands** (queue connector). **Worker** dequeues, runs the same step order (or consumes events in choreographed variant). **Storage** then **Notifier** (async) for callback/poll consistency.
