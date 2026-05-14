# Assignment Submission: Lecture 6 - Reusability and Interfaces

**Student Name:** Sonia Mangane  

**Submission Date:** 19 March 2026  

---

## Overview

For this assignment, I worked on redesigning the `pdf-parse` library.  
The original library was more like a monolithic class, so I tried to break it down using concepts like Information Hiding and Explicit Interfaces.

I separated:
- how the PDF is loaded  
- how the parsing session is managed  
- how data is extracted  

This makes the system easier to reuse in different environments like Node.js, browsers, or even CLI tools.

---

## Files Included

### 1. Analysis & Redesign 

- **part1_reusability_analysis.md**  
  I analyzed the current library and pointed out issues like platform leakage (e.g. Node-only features showing up everywhere) and how that affects reusability.

- **part1_interface_design.md**  
  I designed new interfaces like `IPDFSource` and `IPDFExtractor` and explained their contracts (what they expect and what they return).

- **part2_api_design.md**  
  I designed a REST API based on the Principle of Least Surprise, so the endpoints are simple and predictable.

- **part2_api_architecture.xml**  
  A diagram showing how the API layer sits on top of the library and hides internal implementation details.


- **part3_context_usage.md**  
  I included example code to show that the extraction logic stays the same even if the platform (Node vs browser) changes.

- **part4_component_diagram.xml**  
  A visual diagram of the redesigned components and how they connect to each other.

---


## Key Highlights

- **Separation of Concerns with `IPDFSource`:**  
  By introducing a separate interface for loading PDFs, the parser doesn’t need to know where the file comes from (URL, file system, etc.). This improves reusability a lot.

- **Small Interfaces & Uniform Access:**  
  Instead of one big class, I used a simple `extract()` pattern. This means users only use what they need (e.g. just text) without loading unnecessary features.

- **Information Hiding:**  
  The parsing session is treated like a “black box”. This means we can change the internal implementation later (e.g. switch PDF engines) without affecting users.

- **No Platform Leakage:**  
  I made sure Node.js-specific features like `getHeader()` are not exposed in the browser version. This keeps the API clean and avoids confusion.

---