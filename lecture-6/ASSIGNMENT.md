# Assignment: Redesign pdf-parse Library for Reusability

## Overview

This assignment requires you to **redesign the architecture** of the [pdf-parse](https://www.npmjs.com/package/pdf-parse) npm library, applying **Chapter 6: Reusability and Interfaces** best practices. You will propose a cleaner interface design, document contracts, and show how the redesign improves reusability across Node.js, browser, and CLI contexts.

**Reference:** [pdf-parse v2.4.5](https://www.npmjs.com/package/pdf-parse) – Pure TypeScript module for extracting text, images, and tables from PDFs. Supports Node.js, browser, CJS/ESM, and CLI.

## Learning Objectives

By completing this assignment, you will:
- Analyze an existing library for reusability issues
- Apply interface design principles (minimal, stable, clear)
- Propose a modular architecture with separable concerns
- **Design how to expose pdf-parse as an HTTP/REST API service**
- Document interface contracts and API design
- Support multiple platforms (Node, browser, CLI, API) through abstraction
- Propose versioning and evolution strategy

## Current pdf-parse API (Summary)

- **Entry:** `PDFParse` class with `new PDFParse({ url | data, password?, verbosity?, ... })`
- **Methods:** `getText()`, `getInfo()`, `getScreenshot()`, `getImage()`, `getTable()`, `getHeader()` (Node only), `destroy()`
- **Inputs:** URL, Buffer, base64
- **Outputs:** Text, metadata, page images, embedded images, tables
- **Platforms:** Node.js, browser, Next.js, Vercel, Lambda, Cloudflare Workers

## Part 1: Analysis and Interface Design

### Task 1.1: Reusability Analysis

**Objective:** Identify reusability strengths and weaknesses in the current API.

**Requirements:**
1. Analyze the current pdf-parse API and document:
   - **Strengths:** What supports reusability? (e.g. cross-platform, multiple input sources)
   - **Weaknesses:** What hurts reusability? (e.g. monolithic class, platform-specific methods mixed in, unclear contracts)
   - **Interface issues:** Inconsistencies, too many options in one method, unclear pre/post conditions

2. Reference at least 3 methods (e.g. `getText`, `getImage`, `getHeader`) with concrete observations.

**Deliverable:** `part1_reusability_analysis.md`

**Grading:** 20 points

---

### Task 1.2: Redesigned Interface Proposal

**Objective:** Propose a cleaner, more reusable interface architecture.

**Requirements:**
1. Propose a **modular design** that separates:
   - **Data source** – How PDF is loaded (URL, Buffer, base64) – consider `IPDFSource` or `LoadParameters`
   - **Parsing/session** – Create a parser session from a source – consider `IPDFParser` or `PDFSession`
   - **Extraction operations** – getText, getInfo, getImage, getTable, getScreenshot – consider whether these share a common pattern (e.g. `IExtractor<T>` or a single `extract(op, params)` interface)

2. Define **at least 2 interfaces** (e.g. `IPDFSource`, `IPDFExtractor`) with:
   - Method names and signatures (pseudocode or TypeScript/Python)
   - Documented contracts (preconditions, postconditions)
   - Rationale for the split

3. Show how your design:
   - Supports Node.js and browser (e.g. `getHeader` only in Node module)
   - Allows swapping implementations (e.g. different renderer for `getScreenshot`)
   - Reduces coupling between loading, parsing, and extraction

**Deliverables:**
- `part1_interface_design.md` – Interface definitions, contracts, rationale
- `part1_interfaces.pdf` or `.drawio` – Optional: visual interface diagram

**Grading:** 30 points

---

## Part 2: Exposing pdf-parse as an API

### Task 2.1: API Design

**Objective:** Design how to expose the pdf-parse library as an HTTP/REST API service.

**Requirements:**
1. Define **API endpoints** that map library operations to HTTP:
   - **Input:** How does the client provide the PDF? (e.g. `POST /parse` with multipart file upload, or `POST /parse` with `{ "url": "..." }` or base64 in JSON)
   - **Output:** Extract text, info, images, tables, screenshots – propose one endpoint per operation or a unified endpoint with `action` parameter
   - Example endpoints (adapt as needed):
     - `POST /api/v1/extract/text` – body: file or `{ url }`, response: `{ text, pages }`
     - `POST /api/v1/extract/info` – metadata
     - `POST /api/v1/extract/images` – embedded images (base64 or URLs)
     - `POST /api/v1/extract/tables` – tabular data
     - `POST /api/v1/screenshot` – render pages as PNG (optional params: pages, scale)

2. Define **request/response format** (JSON schema or example):
   - Request: file upload vs URL vs base64
   - Response: structure for each operation (text, metadata, images, tables)
   - Error responses: 400 (bad PDF), 413 (file too large), 422 (parse error), 500

3. Document **design decisions**:
   - Sync vs async (long-running jobs for large files?)
   - Size limits, timeouts
   - Optional: authentication, rate limiting

**Deliverable:** `part2_api_design.md` – Endpoints, request/response format, rationale

**Grading:** 30 points

---

### Task 2.2: API Architecture Diagram

**Objective:** Show how the API wraps the library.

**Requirements:**
1. Create a **component/architecture diagram** (draw.io) showing:
   - **API Layer** – HTTP server, routes, request validation
   - **Service/Business Layer** – PDF parsing service that uses pdf-parse
   - **Library** – pdf-parse (or your redesigned interface)
   - **Clients** – Web app, mobile app, CLI (via curl), batch job
   - Data flow: Client → API → Service → Library → Response

2. Show:
   - Where file upload is handled
   - Where the library is invoked
   - Optional: queue/worker for async processing

**Deliverables:**
- `part2_api_architecture.drawio`
- `part2_api_architecture.png`

**Grading:** 20 points

---

## Part 3: Reusability Across Contexts

### Task 3.1: Usage in Multiple Contexts

**Objective:** Show how the redesigned API is used in Node, browser, and CLI.

**Requirements:**
1. Write **usage examples** (pseudocode or real code) for **at least 2 contexts**:
   - **Node.js server** – e.g. parse PDF from URL, extract text
   - **Browser** – e.g. parse from file input, render first page
   - **CLI** – e.g. `pdf-parse extract-text input.pdf`

2. For each context:
   - Same core interface (e.g. `IPDFExtractor` or `PDFParse`)
   - Only construction/configuration differs (worker path, platform-specific loader)
   - No context-specific methods in the core interface

3. Include **API usage** as one context (e.g. client calling your REST API).

4. Document in `part3_context_usage.md`:
   - How each context uses the same interface
   - What is abstracted (worker, loader, platform)
   - What you avoided to keep the core API reusable

**Deliverable:** `part3_context_usage.md` (with code snippets)

**Grading:** 20 points

---

### Task 3.2: Platform Abstraction (Node vs Browser)

**Objective:** Design how Node-specific features (e.g. `getHeader`) stay out of the core interface.

**Requirements:**
1. Propose how to separate:
   - **Core interface** – Works in Node and browser (e.g. `getText`, `getInfo`, `getImage`, `getTable`, `getScreenshot`)
   - **Node-specific** – e.g. `getHeader` (HTTP range request, no full download)

2. Options to consider (choose one or combine):
   - Submodule: `pdf-parse` (core) vs `pdf-parse/node` (Node extras)
   - Optional capability interface: `INodePDFUtils` with `getHeader`
   - Platform detection and conditional export

3. Document in `part3_platform_abstraction.md`:
   - Your chosen approach
   - How a browser user never depends on Node code
   - How a Node user can opt in to `getHeader`

**Deliverable:** `part3_platform_abstraction.md`

**Grading:** 10 points

---

## Part 4: Evolution and Versioning

### Task 4.1: v1 → v2 Migration and Future Evolution

**Objective:** Propose evolution and versioning strategy.

**Requirements:**
1. The real pdf-parse changed from v1 (function) to v2 (class):
   ```js
   // v1: pdf(buffer).then(r => r.text)
   // v2: new PDFParse({ data }).getText()
   ```
   Propose:
   - How to deprecate v1 cleanly (warnings, migration guide)
   - What v2 improves for reusability (e.g. instance lifecycle, `destroy()`, configurable worker)

2. Propose **one backward-compatible evolution** for a future v2.5 or v3:
   - e.g. Add optional `stream` option to `getText` for large files
   - e.g. Add `getLinks()` with optional param `followExternal: boolean`
   - Document: what changes, what stays compatible, migration notes

**Deliverable:** `part4_evolution.md`

**Grading:** 10 points

---

### Task 4.2: Component Diagram (Required)

**Objective:** Visualize the redesigned architecture.

**Requirements:**
1. Create a **component diagram** (draw.io) showing:
   - Core components: Source Loader, Parser Session, Extractors (Text, Image, Table, Screenshot, Info)
   - Platform modules: Core (shared), Node (getHeader, etc.), Browser (worker config)
   - Interfaces between components
   - How Node and browser consumers use the same core

2. Include a short legend and annotations.

**Deliverables:**
- `part4_component_diagram.drawio`
- `part4_component_diagram.png`

**Grading:** 10 points

---

## Submission Requirements

### Submission Method

GitHub Pull Request. See `../lecture-3/SUBMISSION_GUIDE.md` if needed.

### File Structure

```
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
├── code/                          # Optional: interface stubs or API spec
│   └── README.md
└── README.md
```

### Optional: Code Stubs

You may add minimal interface definitions (TypeScript, Python, or pseudocode) in `code/` to illustrate your design. Full implementation is **not** required.

---

## Grading Rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Reusability analysis | 20 |
| Part 1 | Redesigned interface proposal | 30 |
| Part 2 | API design (endpoints, request/response) | 30 |
| Part 2 | API architecture diagram | 20 |
| Part 3 | Usage in multiple contexts (incl. API client) | 20 |
| Part 3 | Platform abstraction | 10 |
| Part 4 | Evolution and versioning | 10 |
| Part 4 | Component diagram | 10 |
| **Total** | | **150** |

### Quality Criteria

- **Analysis:** Concrete, grounded in the real pdf-parse API
- **Interface design:** Minimal, stable, clear separation of concerns
- **API design:** Clear endpoints, request/response format, rationale
- **API architecture:** How the API wraps the library, data flow
- **Reusability:** Same core used in Node, browser, CLI, and via API
- **Platform abstraction:** Node-specific features isolated from core
- **Documentation:** Clear contracts, rationale, and migration notes

---

## Getting Started

1. **Study pdf-parse:** [npm](https://www.npmjs.com/package/pdf-parse), [GitHub](https://github.com/mehmet-kozan/pdf-parse), [docs](https://mehmet-kozan.github.io/pdf-parse/)
2. **Review lecture examples:** `example1_interface_design_and_contracts.py`, `example2_reusability_and_versioning.py`
3. **Outline interfaces first:** Source → Parser → Extractors
4. **Sketch component diagram** early to guide the design

---

## Reference: pdf-parse Methods

| Method | Description | Platform |
|--------|-------------|----------|
| `getText(params?)` | Extract text | Node, browser |
| `getInfo(params?)` | Metadata, page info | Node, browser |
| `getScreenshot(params?)` | Render pages as PNG | Node, browser |
| `getImage(params?)` | Extract embedded images | Node, browser |
| `getTable(params?)` | Extract tabular data | Node, browser |
| `getHeader(url, validate?)` | HTTP headers, magic bytes | Node only |
| `destroy()` | Free resources | Node, browser |

**Load options:** `url`, `data` (Buffer), `base64`, `password`, `verbosity`, etc.

---

## Deadline

**Due date:** [To be announced by instructor]

**Submission:** GitHub Pull Request to `arch-course-cu/lecture-6/submissions/YOUR_NAME/`

Good luck.
