# Assignment Submission: Lecture 7

**Student Name**: Kagontle Booysen 
**Student ID**: 30009255
**Submission Date**: 27/03/2026

---

## Overview

This submission designs a **Composable Document Processing Pipeline** as required by the Lecture 7 assignment on Composability and Connectors. The pipeline accepts documents (PDF, images, DOCX) and runs them through five sequential stages — Validate → Extract → Classify → Store → Notify — supporting both a synchronous "process and return result" mode and an asynchronous "process in background and notify when done" mode.

The submission covers all three parts: component and connector design with a diagram, orchestration and choreography designs with a comparison and recommendation, and a full REST API specification for both interaction modes.

---

## Files Included

| File | Part | Description |
|------|------|-------------|
| `part1_components_and_connectors.md` | Part 1, Task 1.1 | Full component decomposition (6 components, 12 connectors) with inputs/outputs, sync/async classification, idempotency design, error propagation, and schema versioning |
| `part1_component_connector_diagram.drawio` | Part 1, Task 1.2 | Editable draw.io C&C diagram — all components, all connectors labelled with type and sync/async, legend included |
| `part1_component_connector_diagram.png` | Part 1, Task 1.2 | PNG export of the C&C diagram for quick reference |
| `pipeline_cc_diagram.html` | Part 1, Task 1.2 | Self-contained interactive HTML version of the diagram with hover effects and dark mode support |
| `part2_orchestration.md` | Part 2, Task 2.1 | Orchestrated pipeline design — orchestrator identity, exact call sequence, retry/error/abort handling, one advantage and one disadvantage |
| `part2_choreography.md` | Part 2, Task 2.2 | Choreographed pipeline design — full event catalogue (10 events), per-component subscribe/publish tables, emergent flow diagram, one advantage and one disadvantage |
| `part2_comparison.md` | Part 2, Task 2.3 | Comparison table (7 criteria), hybrid recommendation with pipeline-specific justification, three-way summary table |
| `part3_api_design.md` | Part 3, Task 3.1 | Full REST API specification — 4 endpoints with request/response schemas, sync path component trace, async path event chain, error handling table |

---

## Key Highlights

- **Dual-interface component design** — the Extractor and Classifier each expose a synchronous REST interface (used by the Gateway on the fast-lane sync path) and an asynchronous queue/event interface (used on the async path), sharing the same core implementation. This avoids maintaining two separate codebases while supporting both interaction modes.

- **Hybrid orchestration/choreography recommendation** — neither pure pattern is recommended. The event bus (choreography) handles all component-to-component processing for scalability and failure isolation; a thin lifecycle layer (orchestration) tracks job status centrally for debuggability. This is justified directly against the pipeline's characteristics: OCR variability, burst batch traffic, and the need for a single-lookup audit trail during incident response.

- **Production-grade cross-cutting concerns** — idempotency is designed at every async consumer (Redis cache, DB upsert, delivered-set), error propagation follows a consistent `*.failed` event pattern with dead-letter handling, schema versioning is embedded in every event payload, and the sync path includes an automatic async downgrade on timeout so the client is never left hanging.

---

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net) (File → Open From → Device) to see the fully editable component and connector diagram
2. View `.png` files for a quick non-editable reference of the same diagram
3. Open `pipeline_cc_diagram.html` in any browser for an interactive version of the diagram with hover effects
4. Read `.md` files in any Markdown viewer — GitHub, VS Code, Typora, or any text editor
