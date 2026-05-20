# Assignment Submission: Lecture 8 (Task Board API)

**Student Name**: Kaleb Gebretsadik  
**Student ID**: [30008744]  
**Submission Date**: [4/10/2026]

## Overview
This submission covers the comprehensive analysis and architectural planning for maintaining the "Task Board API" under changing constraints. It applies the principles of **Chapter 8: Compatibility and Coupling**, focusing strictly on minimizing tight dependencies, identifying breakage risks, establishing a graceful HTTP version coexistence pattern, and documenting a rigid deprecation policy.

## Files Included

### Part 1: Coupling Analysis
- `part1_coupling_analysis.md`: Detailed breakdown mapping the data, temporal, and spatial coupling footprints across the Web SPA, Mobile Apps, external Partners, Gateway, API, DB, and Notification systems.
- `part1_coupling_diagram.drawio` / `.png`: A visual coupling flowchart highlighting intentionally dense boundaries (DB) vs loosely targeted dependencies (Queues).

### Part 2: Compatibility and Versioning
- `part2_compatibility_changes.md`: Meticulous classification of incoming feature requests (A-E) determining whether they force a `MAJOR` vs `MINOR` semantic release, accompanied by their contextual semantic risk factors (e.g. silent partner failures).
- `part2_version_coexistence.md`: The migration plan detailing a Gateway-level global path prefix (`/v1` vs `/v2`) paired with an inner-service Translation Adapter to seamlessly maintain legacy payloads during sunsetting phases.

### Part 3: Policy and Migration Story
- `part3_compatibility_policy.md`: The formalized developer governance contract mapping out exact deprecation windows, rigid Error formatting guarantees, and specific protections for third-party Partners versus First-Party Apps.
- `part3_migration_sequence.drawio` / `.png`: A UML sequence diagram demonstrating exactly how the Gateway splits traffic and how the legacy V1 Adapter dynamically fakes/maps data requirements to preserve the core V2 database flow.

## Key Highlights
- **Intelligent Translation Adapters:** Rather than duplicating database columns or writing complex dual-write abstractions, the coexistence architecture maps `/v1/` payload needs dynamically back to the core data formats.
- **Strict Semantic Risk Analysis:** Evaluated feature requests beyond basic JSON compatibility logic—demonstrating how silently dropping length limits creates systemic workflow breakage for unmonitored partner bots.

## How to View
1. Read `.md` files for textual analysis and semantic classification rationales.
2. View `.png` files for quick structural reference.
3. Open `.drawio` files via the native VS Code extension or [draw.io](https://app.diagrams.net/) to inspect/edit the visual designs.
