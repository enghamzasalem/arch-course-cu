# Assignment Submission – Lecture 6

**Student Name:** Amaan Shaikh  
**Submission Date:** 20/03/2026  

---

## Description

This assignment presents a redesigned architecture for the **pdf-parse** library with the goal of improving reusability, modularity, and clarity of interfaces.  
The redesign separates the responsibilities of loading data, managing parser sessions, and performing extraction operations.  

The submission also includes a REST API design, diagrams of the architecture, examples of usage in different environments, and a versioning strategy for future development.

---

## Included Files

- `part1_reusability_analysis.md`  
  Analysis of the current pdf-parse API, including strengths, weaknesses, and interface problems.

- `part1_interface_design.md`  
  Proposed interface redesign with contracts, method definitions, and explanation of design decisions.

- `part2_api_design.md`  
  Design of the REST API including endpoints, request/response format, and error handling.

- `part2_api_architecture.drawio`  
  Editable draw.io diagram showing the API architecture.

- `part2_api_architecture.png`  
  Image version of the API architecture diagram.

- `part3_context_usage.md`  
  Examples of how the redesigned interface is used in Node.js, browser, CLI, and API contexts.

- `part3_platform_abstraction.md`  
  Explanation of how Node-specific functionality is separated from the core interface.

- `part4_evolution.md`  
  Description of version changes from v1 to v2 and a proposal for future improvements.

- `part4_component_diagram.drawio`  
  Editable draw.io component diagram of the redesigned architecture.

- `part4_component_diagram.png`  
  Image version of the component diagram.

- `README.md`  
  Overview of the submission and file structure.

---

## Main Design Goals

- Create a **modular interface architecture**
- Separate **source loading, parsing session, and extraction**
- Keep the **core interface platform-independent**
- Allow usage in **Node.js, browser, CLI, and REST API**
- Support future changes without breaking existing code

The redesign introduces clear responsibilities for each component and makes the library easier to reuse in different environments.

---

## Important Notes

- The `.drawio` files can be opened and edited using draw.io.
- The `.png` files are provided for quick viewing.
- All `.md` files contain explanations and design documentation.

This submission focuses on **interface design and architecture**, not on full implementation.