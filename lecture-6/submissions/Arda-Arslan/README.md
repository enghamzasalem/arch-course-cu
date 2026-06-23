# Assignment Submission: Lecture 6

**Student Name**: Arda Arslan  
**Student ID**: 30008610  
**Submission Date**: 19/03/2026  

## Overview

This submission redesigns the pdf-parse library to improve reusability through a modular interface architecture. It includes a reusability analysis, a separation of source, session, and extraction concerns, a REST API design, architecture and component diagrams, cross-platform usage examples (Node.js, browser, API), platform abstraction for Node-specific features, and a versioning strategy for future evolution.

## Files Included

- `part1_reusability_analysis.md` — Analysis of strengths, weaknesses, and interface issues in the current pdf-parse API
- `part1_interface_design.md` — Proposed modular interface design with contracts and rationale
- `part2_api_design.md` — REST API endpoints, request/response formats, and design decisions
- `part2_api_architecture.drawio` — API architecture diagram (draw.io)
- `part2_api_architecture.png` — API architecture diagram (image)
- `part3_context_usage.md` — Usage examples in Node.js, browser, and API contexts
- `part3_platform_abstraction.md` — Separation of core and Node-specific functionality
- `part4_evolution.md` — v1→v2 migration and future evolution proposal
- `part4_component_diagram.drawio` — Component diagram (draw.io)
- `part4_component_diagram.png` — Component diagram (image)
- `README.md` — This file

## Key Highlights

- Modular architecture separating **IPDFSource, IPDFSession, and IPDFExtractor<T>** for better reusability and separation of concerns
- Same core interface reused across **Node.js, browser, CLI, and API contexts** 
- Clear separation of **platform-independent core** and **Node-specific features (getHeader)**  
- REST API design mapping library operations to HTTP endpoints with consistent structure 
- Evolution strategy with backward compatibility and clean deprecation (v1 -> v2) 

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams  
2. View `.png` files for quick reference  
3. Read `.md` files for detailed documentation