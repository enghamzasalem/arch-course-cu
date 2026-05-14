# Part 2.3 — Comparison and recommendation

| Criterion | Orchestration | Choreography |
|-----------|-----------------|--------------|
| Change pipeline order | Edit orchestrator / API; **central** change | Republish routing or subscriber filters; risk of **inconsistent** interim deployments |
| Add a new step | One new call (or branch) in orchestrator | New service + subscribe/publish contracts; **less coupling** to existing steps |
| Debugging / tracing | Single trace span chain from one coordinator | **Correlation IDs** required across bus and services |
| Latency (conceptual) | Fewer hops if in-process; extra if chatty RPC | Event persistence + dispatch adds **latency** vs direct call |
| Scalability | Coordinator tier must scale; workers vertical to orchestrator | **Horizontal** scale per consumer group |

## Recommendation

Use a **hybrid**: **orchestration** for the **synchronous** path (strict SLA, simple mental model) and **choreography over a queue/event bus** for **async** jobs (OCR-heavy, batch, webhook completion). Shared **Validator** and **Storage** abstractions stay the same; only the **composition style** differs by entry mode.
