# Document Processing Pipeline — Assignment Submission

## File Map

```
submissions/shreyash-ahir/
├── part1_components_and_connectors.md      6 components + 7 connectors with justification
├── part1_component_connector_diagram.drawio
├── part1_component_connector_diagram.png
├── part2_orchestration.md                  Orchestrator: call sequence, retries, trade-offs
├── part2_choreography.md                   Event catalogue, component pub/sub, trade-offs
├── part2_comparison.md                     Comparison table + hybrid recommendation
├── part3_api_design.md                     Sync + async REST endpoints, error format, limits
├── part3_sequence_diagram.drawio           Async flow: Client -> Queue -> Worker -> Notify
├── part3_sequence_diagram.png
└── README.md
```

## Key Design Decisions

- **Validate sync**: cheap and must fail-fast before expensive OCR.
- **Queue between upload and processing**: decouples HTTP thread from CPU-heavy work.
- **Orchestration inside the worker**: keeps retry logic and pipeline order in one place.
- **Async notify queue**: Notifier retries webhook independently of the processing worker.
- **Hybrid recommendation**: orchestrated core (Validate/Extract/Classify/Store) + choreographed periphery (enqueue, notify).
