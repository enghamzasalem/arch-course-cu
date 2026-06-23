# Part 2.3 – Comparison and Recommendation

## Comparison Table

| Criterion | Orchestration | Choreography |
|---|---|---|
| Changing pipeline order | Easy - update sequence in one place | Hard - requires re-wiring subscriptions across components |
| Adding new steps | Easy - insert a new call in the orchestrator | Easy - subscribe to an existing event and publish a new one |
| Debugging and tracing | Easy - full job state in one place | Hard - must correlate events across multiple components |
| Latency | Slightly higher - orchestrator adds a coordination hop | Lower - components react directly to events |
| Scalability | Orchestrator can become a bottleneck | High - components scale independently |

## Recommendation

A **hybrid approach** is recommended. Orchestration is used for the path Validator → Extractor → Classifier → Storage where predictable sequencing, error handling, and job traceability matter most. Choreography is used at the edges - the Notifier subscribes to `StorageComplete` and failure events independently, so notification logic never couples back into the orchestrator. This gives the pipeline a single traceable flow for the critical processing steps while keeping peripheral concerns like notification decoupled and easy to extend.