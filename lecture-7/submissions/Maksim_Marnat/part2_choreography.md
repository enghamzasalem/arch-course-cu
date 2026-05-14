# Part 2.2 — Choreographed (event-driven) design

## Events

| Event | Payload (conceptual) |
|-------|----------------------|
| `DocumentReceived` | `job_id`, blob ref, options |
| `ValidationPassed` | `job_id`, metadata |
| `ValidationFailed` | `job_id`, reason |
| `ExtractionComplete` | `job_id`, text, layout |
| `ClassificationComplete` | `job_id`, label, confidence |
| `DocumentStored` | `job_id`, URIs |
| `PipelineCompleted` | `job_id`, summary |

(No central orchestrator; services react to events.)

## Subscriptions and publications

| Component | Subscribes | Publishes |
|-----------|------------|-----------|
| **Pipeline API** | — | `DocumentReceived` after upload accepted |
| **Validator** | `DocumentReceived` | `ValidationPassed` / `ValidationFailed` |
| **Extractor** | `ValidationPassed` | `ExtractionComplete` |
| **Classifier** | `ExtractionComplete` | `ClassificationComplete` |
| **Storage** | `ClassificationComplete` | `DocumentStored` |
| **Notifier** | `DocumentStored` | `PipelineCompleted` (or emits only outbound webhook) |

Flow emerges: Validator never calls Extractor; it only publishes.

## Trade-offs

- **Advantage:** **Scale and replace** steps independently; new consumers (e.g. audit) subscribe without changing producers.
- **Disadvantage:** **End-to-end behavior** is distributed; debugging needs correlation on `job_id` across many services and the event bus.
