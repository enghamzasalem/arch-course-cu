# Part 3 – Task 3.1: Usage in Multiple Contexts

## Overview

This document demonstrates how the redesigned pdf-parse architecture can be used across multiple contexts while maintaining a **consistent core interface**. The same abstractions (`IPDFSource`, `IPDFParser`, `IPDFSession`, `IPDFExtractor`) are reused, with only configuration differences per environment.

Contexts covered:

* Node.js server
* Browser application
* CLI tool
* REST API client

---

## 1. Core Design Principle

All contexts rely on the same workflow:

```
Source → Parser → Session → Extractor → Result
```

Only the **source implementation and environment configuration** differ.

---

## 2. Node.js Server Usage

### Scenario

Parse a PDF from a URL and extract text.

```ts
import { URLSource, PDFParser, TextExtractor } from "pdf-parse";

const source = new URLSource("https://example.com/sample.pdf");
const parser = new PDFParser();

const session = await parser.createSession(source);

const extractor = new TextExtractor();
const text = await extractor.extract(session);

await session.destroy();

console.log(text);
```

### Key Points

* Uses `URLSource`
* Runs in Node.js environment
* Same extractor interface as other contexts

---

## 3. Browser Usage

### Scenario

User uploads a PDF file and extracts text.

```ts
import { BufferSource, PDFParser, TextExtractor } from "pdf-parse";

const fileInput = document.getElementById("fileInput");

fileInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  const arrayBuffer = await file.arrayBuffer();

  const source = new BufferSource(arrayBuffer);
  const parser = new PDFParser({ worker: true });

  const session = await parser.createSession(source);

  const extractor = new TextExtractor();
  const text = await extractor.extract(session);

  await session.destroy();

  console.log(text);
});
```

### Key Points

* Uses browser-compatible source (`ArrayBuffer`)
* Worker-based parsing for performance
* No Node-specific APIs used

---

## 4. CLI Usage

### Scenario

Command-line tool to extract text from a local PDF file.

```ts
#!/usr/bin/env node

import fs from "fs";
import { BufferSource, PDFParser, TextExtractor } from "pdf-parse";

const filePath = process.argv[2];

const buffer = fs.readFileSync(filePath);
const source = new BufferSource(buffer);

const parser = new PDFParser();
const session = await parser.createSession(source);

const extractor = new TextExtractor();
const text = await extractor.extract(session);

await session.destroy();

console.log(text);
```

### Key Points

* Uses file system (Node-specific outside core)
* Core API remains unchanged
* CLI is just a thin wrapper

---

## 5. REST API Client Usage

### Scenario

Client calls the API to extract text.

```ts
const response = await fetch("/api/v1/extract/text", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    url: "https://example.com/sample.pdf"
  })
});

const data = await response.json();
console.log(data.text);
```

### Key Points

* Client does not interact with core interfaces directly
* Uses HTTP abstraction
* Internally mapped to same architecture

---

## 6. Abstraction Analysis

| Aspect               | Abstracted | How                          |
| -------------------- | ---------- | ---------------------------- |
| Data loading         | Yes        | `IPDFSource` implementations |
| Parsing              | Yes        | `IPDFParser` + session       |
| Extraction           | Yes        | `IPDFExtractor`              |
| Platform differences | Yes        | External to core interfaces  |

---

## 7. What Was Avoided (for Reusability)

* ❌ No platform-specific methods in core interfaces
* ❌ No direct file system or DOM dependencies
* ❌ No mixed responsibilities (loading + extraction)

---

## 8. Benefits of Unified Interface

### 8.1 Consistency

* Same API across all environments

### 8.2 Reusability

* Code patterns transferable between contexts

### 8.3 Maintainability

* Changes in core affect all contexts uniformly

---

## 9. Conclusion

The redesigned architecture ensures that:

* A **single core interface** supports all environments
* Only configuration differs per context
* The system remains **modular, reusable, and scalable**

This demonstrates strong adherence to interface design and reusability principles.
