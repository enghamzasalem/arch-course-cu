# Assignment Submission: Lecture 6

**Student Name:** Kagontle-Booysen 
**Student ID:** 30009255
**Submission Date:** 20/03/2026  

## Overview
This submission presents a redesign of the `pdf-parse` npm library architecture based on the principles in **Chapter 6: Reusability and Interfaces**. The work evaluates the current design of `pdf-parse v2.4.5`, identifies strengths and weaknesses affecting reusability, and proposes a cleaner, more modular interface design.

The redesigned architecture focuses on improving separation of concerns, interface clarity, contract documentation, and cross-platform reuse. The proposal shows how the library can better support use across Node.js, browser, and CLI environments while reducing platform-specific coupling and making the system easier to extend, test, and maintain.

## Files Included
* **`README.md`** – Summary of the Lecture 6 submission.
* **`part1_reusability_analysis.md`** – Analysis of the current `pdf-parse` architecture using Chapter 6 reusability principles.
* **`part2_redesigned_architecture.md`** – Proposed redesigned architecture and modular interface structure.
* **`part3_method_contracts.md`** – Documented contracts for selected methods, including preconditions, postconditions, and error cases.
* **`part4_cross_platform_examples.md`** – Examples showing how the redesign improves reuse in Node.js, browser, and CLI contexts.
* **`architecture_diagram.drawio`** – Editable architecture diagram of the redesigned solution.
* **`architecture_diagram.png`** – Exported version of the architecture diagram for quick viewing.

## Key Highlights
* Evaluates `pdf-parse` against Chapter 6 reusability and interface design principles.
* Identifies major reusability issues such as monolithic design, mixed platform-specific methods, and unclear method contracts.
* Proposes a modular redesign with focused components and clearer responsibilities.
* Documents explicit method contracts to improve predictability and reuse.
* Demonstrstrates how the redesign supports Node.js, browser, and CLI usage more effectively.

## How to View
1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to view and edit the diagrams.
2. View `.png` files for quick diagram reference.
3. Read `.md` files for the analysis, redesign, and contract documentation.
4. Review the usage examples to understand how the redesigned architecture improves reusability across platforms.
