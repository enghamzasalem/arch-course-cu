# Assignment Submission: Lecture 7

**Student Name**: Arda Arslan
**Student ID**: 30008610
**Submission Date**: 26/03/2026

## Overview

This submission designs a composable Document Processing Pipeline architecture. It includes component and connector decomposition, both orchestrated and choreographed flow designs, a comparison and hybrid recommendation, a REST API design for sync and async processing, and diagrams for the component-connector view and async sequence flow.

## Files Included

- `part1_components_and_connectors.md` — Component decomposition with responsibilities, inputs/outputs, connector types, and sync/async justification
- `part1_component_connector_diagram.drawio` — Component and connector diagram (draw.io)
- `part1_component_connector_diagram.png` — Component and connector diagram (image)
- `part2_orchestration.md` — Orchestrated pipeline design with sequence of calls and error handling
- `part2_choreography.md` — Event-driven choreographed design with event list and component responsibilities
- `part2_comparison.md` — Comparison of orchestration and choreography with hybrid recommendation
- `part3_api_design.md` — REST API endpoints for sync and async processing with flow mappings
- `part3_sequence_diagram.drawio` — Async end-to-end sequence diagram (draw.io)
- `part3_sequence_diagram.png` — Async end-to-end sequence diagram (image)
- `README.md` — This file

## Key Highlights

- Pipeline decomposed into **6 components** with clear responsibilities and both sync and async connector paths
- **Orchestrated design** uses Pipeline API as central coordinator for clear flow control
- **Choreographed design** uses event-driven communication with no central orchestrator
- **Hybrid recommendation** combining orchestration for sync path and choreography for async path
- REST API supports both **immediate processing** and **background job submission** with webhook callback

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for detailed documentation