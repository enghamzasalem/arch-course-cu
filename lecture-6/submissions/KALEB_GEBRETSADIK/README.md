# Assignment Submission: Lecture 6

**Student Name**: Kaleb Gebretsadik   
**Submission Date**: March 19, 2026

## Overview

This assignment provides a complete architectural redesign of the `pdf-parse` npm library, applying the "Chapter 6: Reusability and Interfaces" best practices. The monolithic class structure was broken down into a decoupled, highly modular tool set (`IPDFSource`, `IPDFSession`, `IExtractor<T>`).

## Files Included

### Part 1: Analysis and Interface Design
- `part1_reusability_analysis.md`: Strengths, weaknesses, and a breakdown of existing interface issues.
- `part1_interface_design.md`: The redesigned modular contracts and rationale.
- `part1_interfaces.drawio` / `.png`: Visual interface diagram (optional).

### Part 2: Exposing pdf-parse as an API
- `part2_api_design.md`: REST API endpoints, request/response formats, and design decisions.
- `part2_api_architecture.drawio` / `.png`: Data flow from clients down to the core library.

### Part 3: Reusability Across Contexts
- `part3_context_usage.md`: Usage examples showing identical core interaction in Node, Browser, and API.
- `part3_platform_abstraction.md`: Demonstrates using `package.json` submodule exports to quarantine Node dependencies.

### Part 4: Evolution and Versioning
- `part4_evolution.md`: The clean v1 to v2 migration strategy and future streaming features.
- `part4_component_diagram.drawio` / `.png`: Component map of the entire redesigned architecture.

## Key Highlights

- **Decoupled Architecture:** Extractor logic is isolated into plugins, meaning someone using `pdf-parse` for text never pays the module weight/memory for image parsing.
- **REST API Boundaries:** A clean, synchronous HTTP interface mimicking enterprise service endpoints with file limits and rate validation.
- **Environment Agnostic:** Fully guarantees that a frontend React developer will never see an `http` or `fs` import error by strictly organizing Node layers away from the root exports.

## How to View

1. Read `.md` files for textual analysis and code contracts.
2. View `.png` files for quick diagram reference.
3. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable models.
