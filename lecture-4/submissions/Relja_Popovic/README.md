# Assignment Submission: Lecture 4

**Student Name**: Relja Popovic
**Student ID**: 30008800 
**Submission Date**: 05/03/2026

## Overview

Architecture models for a video streaming platform, covering three levels of C4 diagrams and two UML diagrams, plus model documentation.

## Files Included

**Part 1 – C4 Model**
- `part1_context_diagram.drawio` / `.png` — System context: 3 user personas and 2 external systems
- `part1_container_diagram.drawio` / `.png` — 5 containers with technology labels and protocols
- `part1_component_diagram.drawio` / `.png` — 4 internal components of the API Service

**Part 2 – UML Diagrams**
- `part2_sequence_diagram.drawio` / `.png` — "User watches a video" flow: 5 participants, 8 messages
- `part2_deployment_diagram.drawio` / `.png` — 4 infrastructure nodes with artifacts and stereotypes

**Part 3 – Documentation**
- `part3_model_documentation.md` — Modeling approach, diagram index, and consistency notes

## Key Highlights

- C4 levels 1–3 nest directly into each other, with consistent element names across all diagrams
- The sequence diagram covers the full watch flow: JWT auth, metadata fetch, CDN signed URL generation, and video delivery
- A shared color palette (blue = client apps, teal = backend, yellow = database, orange = external) is applied consistently across all diagrams

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation