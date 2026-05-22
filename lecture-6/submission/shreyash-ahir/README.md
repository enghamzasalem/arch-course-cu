# pdf-parse Redesign — Assignment Submission

## File Map

```
submissions/YOUR_NAME/
├── part1_reusability_analysis.md     Analysis of current API strengths/weaknesses
├── part1_interface_design.md         IPDFSource, IPDFSession, IPDFExtractor<T> proposal
├── part2_api_design.md               HTTP REST endpoint definitions + error format
├── part2_api_architecture.drawio     draw.io source for API architecture diagram
├── part2_api_architecture.png        Exported PNG
├── part3_context_usage.md            Node, browser, CLI, API client usage examples
├── part3_platform_abstraction.md     getHeader isolation via submodule exports
├── part4_evolution.md                v1→v2 migration + v2.5 streaming proposal
├── part4_component_diagram.drawio    draw.io source for redesigned architecture
├── part4_component_diagram.png       Exported PNG
└── README.md
```

## Key Design Decisions

1. Three-layer interface split: `IPDFSource` / `IPDFSession` / `IPDFExtractor<T>`
2. Generic extractor pattern — new content types added without changing existing interfaces
3. `getHeader` isolated to `pdf-parse/node` submodule using package.json `exports` conditions
4. REST API: one endpoint per operation — enables per-route limits without conditional logic
5. Async job pattern for screenshot of large documents only
6. v1 deprecated via shim + warning, removed in v3.0.0
