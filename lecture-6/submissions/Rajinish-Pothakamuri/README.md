# Assignment: Redesign pdf-parse Library for Reusability

**Course:** Software Architecture  
**Topic:** Chapter 6 – Reusability and Interfaces  
**Library:** [pdf-parse v2.4.5](https://www.npmjs.com/package/pdf-parse)

---

## Overview

This submission redesigns the **pdf-parse** npm library using principles from **reusability and interface design**.

The proposed solution transforms the library from a **monolithic class-based API** into a **modular, interface-driven architecture** that separates:

- Data loading
- Parsing lifecycle management
- Extraction operations

The redesign improves:
- **Reusability** across Node.js, browser, CLI, and API contexts
- **Extensibility** through pluggable extractors
- **Maintainability** via clear separation of concerns
- **Platform independence** with isolated Node-specific features

Additionally, the redesigned architecture is exposed as a **REST API**, enabling usage as a scalable service.

---

## How to Read This Submission

This submission is structured to reflect a logical progression:

1. **Part 1** analyzes the current pdf-parse API and proposes a redesigned interface architecture.
2. **Part 2** exposes the redesigned system as a REST API.
3. **Part 3** demonstrates reusability across multiple execution contexts.
4. **Part 4** defines evolution and versioning strategies.

Each part builds on the previous one, ensuring consistency between analysis, design, and implementation decisions.

---

## Submission Structure

submissions/YOUR_NAME/
├── part1_reusability_analysis.md
├── part1_interface_design.md
├── part2_api_design.md
├── part2_api_architecture.drawio
├── part2_api_architecture.png
├── part3_context_usage.md
├── part3_platform_abstraction.md
├── part4_evolution.md
├── part4_component_diagram.drawio
├── part4_component_diagram.png
└── README.md


---

## Part Summaries

### Part 1 – Analysis and Interface Design

- **Reusability Analysis:** Identifies key weaknesses in the current monolithic `PDFParse` class — tight coupling between loading, parsing, and extraction; mixed platform-specific logic; and missing interface contracts.
- **Interface Proposal:** Introduces a three-layer modular design:
  - `IPDFSource` — abstracts input (URL, Buffer, base64)
  - `IPDFParser` / `IPDFSession` — manages parsing lifecycle
  - `IPDFExtractor<T>` — standardizes extraction operations (text, images, tables, screenshots, metadata)

---

### Part 2 – Exposing pdf-parse as a REST API

- Defines a RESTful API with **operation-specific endpoints** under `/api/v1/`, each mapping directly to a corresponding extraction capability in the redesigned architecture:
  - `POST /extract/text`
  - `POST /extract/info`
  - `POST /extract/images`
  - `POST /extract/tables`
  - `POST /screenshot`
- Supports multipart file upload, URL, and base64 input formats.
- Documents error responses (400, 413, 422, 500), size limits, timeouts, and optional authentication/rate limiting.
- Architecture diagram shows the full data flow from client through API layer, service layer, and library.

---

### Part 3 – Reusability Across Contexts

- Demonstrates the same core interaction pattern (`Source → Parser → Session → Extractor`) across:
  - Node.js
  - Browser
  - CLI
  - REST API client
- Platform abstraction separates core (platform-independent) from Node-specific features (`getHeader`) via a `pdf-parse/node` submodule, ensuring browser consumers never depend on Node code.

---

### Part 4 – Evolution and Versioning

- Documents the v1 (function-based) to v2 (class-based) migration with:
  - Deprecation warnings
  - Migration guide
  - Backward-compatibility shim
- Proposes **streaming text extraction (`extractStream`)** as a backward-compatible enhancement for large PDFs.
- Follows **Semantic Versioning (SemVer)** with clear MAJOR/MINOR/PATCH strategy.

---

## Architecture Summary

The redesigned system follows a layered architecture:

- **Source Layer** → Handles input (URL, Buffer, base64)
- **Parser Layer** → Manages parsing sessions and lifecycle
- **Extraction Layer** → Provides pluggable extractors for different data types
- **API Layer** → Exposes functionality via HTTP endpoints
- **Platform Modules** → Extend functionality (e.g., Node-specific utilities)

This layered approach ensures **low coupling and high cohesion**.

---

## Alignment with Assignment Objectives

| Requirement | How it is Addressed |
|------------|--------------------|
| Reusability analysis | Part 1 identifies strengths and weaknesses of the current API |
| Interface design | Part 1.2 introduces modular interfaces (`IPDFSource`, `IPDFParser`, `IPDFExtractor`) |
| API exposure | Part 2 defines REST endpoints and architecture |
| Multi-context usage | Part 3 demonstrates Node, browser, CLI, and API usage |
| Platform abstraction | Part 3.2 isolates Node-specific functionality |
| Evolution strategy | Part 4 defines migration and future enhancements |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| API style | Multiple endpoints | Better clarity, validation, and mapping to extraction operations |
| Platform separation | Submodule (`pdf-parse/node`) | Browser consumers remain free of Node dependencies |
| Extraction pattern | `IPDFExtractor<T>` per type | Type-safe, pluggable, and independently testable |
| Sync vs async API | Synchronous (async jobs as future enhancement) | Simpler for most use cases; scalable extension available |
| Versioning | SemVer | Industry standard with clear evolution strategy |

---

## Conclusion

This redesign demonstrates how applying **interface-driven design** and **modular architecture** significantly improves the reusability, scalability, and adaptability of a real-world library across multiple platforms and use cases.