# Assignment Submission: Lecture 7 - Composable Document Pipeline

**Student Name**: Kaleb Gebretsadik  
**Student ID**: 30008744  
**Submission Date**: March 27, 2026

## Overview

This submission contains the completed architecture and design for the **Document Processing Pipeline** as assigned in Lecture 7 (Composability and Connectors). The system accepts documents, executes validation, text extraction (OCR), classification, and storage. The design explicitly covers detailed component decomposition, explores the trade-offs between Orchestrated and Choreographed event-driven designs, and delivers a robust API schema for both synchronous and asynchronous workflows.

## Files Included

### Part 1: Component & Connector Design
- `part1_components_and_connectors.md`: Details the 5 core pipeline components, their responsibilities, and heavily justifies the choice between synchronous and asynchronous connectors.
- `part1_component_connector_diagram.drawio`: The editable architecture diagram visualizing components and the communication protocols linking them.
- `part1_component_connector_diagram.png`: The visual export of the Component and Connector diagram.

### Part 2: Orchestration vs Choreography
- `part2_orchestration.md`: Outlines the pipeline using a centralized PipelineOrchestrator, including its execution sequence and error/retry logic.
- `part2_choreography.md`: Redesigns the pipeline to be purely event-driven, mapping out component autonomous pub/sub event reactions.
- `part2_comparison.md`: Provides a side-by-side comparison matrix and issues a final architectural recommendation advocating for a hybrid "Event-Driven Orchestration" approach.

### Part 3: API & Sequence
- `part3_api_design.md`: Proposes the exact REST API endpoint contracts for handling immediate bulk processing (`/run`) versus deferred asynchronous background tasks (`/jobs`).
- `part3_sequence_diagram.drawio`: The editable UML sequence diagram tracing the direct blocking flow of the synchronous API path.
- `part3_sequence_diagram.png`: The visual export of the sequence diagram.

## Key Highlights

- **Dual-Path Support:** The architecture intelligently isolates the synchronous web thread from the heavy asynchronous OCR queues, preventing bottlenecks.
- **Hybrid Recommendation:** A carefully justified recommendation balancing the extreme high-volume scalability of Choreography with the strict observability/tracing benefits of Orchestration.
- **Robust Failure Handling:** Explicit definitions around how transient network failures and validation rejections are managed differently across both orchestrated and event-mapped systems.

