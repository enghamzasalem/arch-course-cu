# Lecture 7: Composability and Connectors

## Overview

This folder contains practical Python examples and one assignment for **Chapter 7: Composability and Connectors**.

The lecture focuses on how components are composed into larger systems and how they communicate through connectors.

## Learning Objectives

By working through these materials, you will:

1. **Component Composition** – Build systems from smaller components
2. **Connector Types** – Direct call, RPC, message queue, event bus, REST
3. **Message Passing** – Sync request/response vs async fire-and-forget
4. **Service Composition** – Compose services into workflows
5. **Event-Driven Architecture** – Publish/subscribe, event bus
6. **Orchestration vs Choreography** – Central coordinator vs distributed control

## Example Files

### `example1_composition_and_connectors.py`

**Concepts:** Composition, connector types, message passing

- Order processing pipeline composed from Inventory, Payment, Shipping, Notifier
- Connector types: direct call (sync) vs message queue (async)
- When to use sync vs async
- Scenario: Order processing

### `example2_orchestration_vs_choreography.py`

**Concepts:** Orchestration, choreography, event-driven

- **Orchestration:** OrderOrchestrator calls services in sequence
- **Choreography:** Event bus; components subscribe to OrderPlaced and react
- Comparison and when to use each
- Scenario: Order fulfillment

## Key Concepts

### Composition

- **System** = Components + Connectors
- Components have clear responsibilities; connectors define how they communicate
- Composition = assembling existing components rather than building one monolith

### Connector Types

| Type          | Sync/Async | Use when                          |
|---------------|------------|------------------------------------|
| Direct call   | Sync       | Same process, need immediate result |
| RPC / REST    | Sync       | Cross-process, request/response    |
| Message queue | Async      | Decouple, scale, defer work        |
| Event bus     | Async      | Pub/sub, many subscribers          |

### Orchestration vs Choreography

- **Orchestration:** One component (orchestrator) controls the flow and calls others
- **Choreography:** No central driver; components react to events
- **Event-driven:** Enables choreography; components publish and subscribe

## Running the Examples

```bash
cd arch-course-cu/lecture-7
python3 example1_composition_and_connectors.py
python3 example2_orchestration_vs_choreography.py
```

## Lecture presentation (PPT-style)

- **`LECTURE_PRESENTATION.html`** — Open in a browser: **Fullscreen** (`F` or button), **Save as PDF** (`P` or button → Print → destination “Save as PDF”). Print uses the same dark layout, one slide per landscape page.
- **`LECTURE_SLIDES_MARP.md`** — Marp source; export to **PowerPoint (.pptx)** with [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) or `npx @marp-team/marp-cli`.
- **Google Slides:** **`GOOGLE_SLIDES_APPS_SCRIPT.gs`** — Paste into Slides **Extensions → Apps Script**, run **`buildLecture7Slides`** to create all slides (see **`GOOGLE_SLIDES_SETUP.md`**). There is no magic URL; Google needs your authorization once.
- **`PRESENTATION_README.md`** — How to use all formats.

## Assignment

See **`ASSIGNMENT.md`**. You will design a **Document Processing Pipeline** as a composable system:

- Decompose into components and define connectors (sync/async)
- Draw component-and-connector diagram
- Design both orchestrated and choreographed (event-driven) versions
- Compare and recommend one (or hybrid)
- Define API for sync and async pipeline execution
- Draw sequence diagram for one flow

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Chapter 5:** Modularity and Components
- **Chapter 6:** Reusability and Interfaces
- **Chapter 8:** Compatibility and Coupling (next lecture)

## Next Steps

After this lecture you will be able to:

- Compose systems from components and connectors
- Choose connector types and justify sync vs async
- Design orchestrated and event-driven (choreographed) flows
- Compare and apply composition patterns
