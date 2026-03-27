# Part 3 – Task 3.2: Platform Abstraction (Node vs Browser)

## Overview

This document defines how the redesigned pdf-parse architecture cleanly separates **platform-independent core functionality** from **Node-specific features**, ensuring maximum reusability across environments.

The goal is to ensure that:

* Core functionality works in both **Node.js and browser**
* Platform-specific features (e.g., `getHeader`) are **isolated and optional**
* Consumers only depend on what they need

---

## 1. Problem in Current Design

In the existing pdf-parse API:

* Node-specific method `getHeader()` exists in the same class as browser-compatible methods
* This leads to:

  * Implicit platform dependency
  * Potential runtime issues in browser
  * Violation of interface segregation principle

---

## 2. Proposed Solution: Modular Platform Separation

### 2.1 Core Module (Platform-Independent)

Package: `pdf-parse`

Contains:

* `IPDFSource`
* `IPDFParser`
* `IPDFSession`
* `IPDFExtractor`
* Core extractors:

  * `TextExtractor`
  * `ImageExtractor`
  * `TableExtractor`
  * `ScreenshotExtractor`
  * `InfoExtractor`

### Characteristics

* No Node.js APIs (fs, http, streams)
* No browser-specific APIs (DOM dependencies)
* Fully portable across environments

---

### 2.2 Node-Specific Module

Package: `pdf-parse/node`

Defines additional capabilities:

```ts
interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<HeaderInfo>;
}
```

### Implementation Example

```ts
class NodePDFUtils implements INodePDFUtils {
  async getHeader(url: string, validate?: boolean): Promise<HeaderInfo> {
    // Uses Node.js HTTP/HTTPS modules
  }
}
```

### Characteristics

* Uses Node-only APIs (HTTP range requests, streams)
* Not bundled in browser builds

---

## 3. Usage Pattern

### 3.1 Browser User

```ts
import { PDFParser, TextExtractor } from "pdf-parse";

// No access to Node-specific utilities
```

✔ Safe: No Node dependencies included

---

### 3.2 Node User (Opt-in)

```ts
import { PDFParser } from "pdf-parse";
import { NodePDFUtils } from "pdf-parse/node";

const utils = new NodePDFUtils();
const header = await utils.getHeader("https://example.com/sample.pdf");
```

✔ Explicit opt-in for Node features

---

## 4. Alternative Approaches Considered

### Option 1: Submodule Separation (Chosen)

* `pdf-parse` (core)
* `pdf-parse/node` (Node extras)

✔ Clear separation
✔ Tree-shakable
✔ No accidental imports

---

### Option 2: Optional Capability Interface

```ts
interface INodeCapable {
  getHeader?: (url: string) => Promise<HeaderInfo>;
}
```

❌ Rejected because:

* Introduces optional methods in core interface
* Breaks interface clarity

---

### Option 3: Runtime Platform Detection

```ts
if (isNode()) {
  // enable getHeader
}
```

❌ Rejected because:

* Hidden behavior
* Harder to test and maintain

---

## 5. Ensuring Browser Independence

The core module ensures:

* No `fs`, `http`, or Node streams
* Uses only:

  * `ArrayBuffer`
  * Web-compatible APIs
* Build tools (e.g., bundlers) exclude Node module

---

## 6. Dependency Structure

```
pdf-parse (core)
   ↑
pdf-parse/node (depends on core)
```

* Core has **zero dependency** on Node module
* Node module extends functionality

---

## 7. Benefits of This Approach

### 7.1 Strong Separation of Concerns

* Core = parsing + extraction
* Node module = network-specific optimizations

### 7.2 Improved Reusability

* Browser apps remain lightweight
* Node apps gain advanced capabilities

### 7.3 Better Maintainability

* Platform-specific code isolated
* Easier testing and debugging

### 7.4 Explicit Capability Model

* Users clearly know what is available
* No hidden or implicit features

---

## 8. Summary

| Aspect                 | Design Choice                      |
| ---------------------- | ---------------------------------- |
| Core functionality     | Platform-independent module        |
| Node-specific features | Separate submodule                 |
| Browser compatibility  | Guaranteed (no Node code)          |
| Extensibility          | Add new platform modules if needed |

---

## 9. Conclusion

The proposed platform abstraction ensures that pdf-parse:

* Maintains a **clean, reusable core interface**
* Avoids mixing platform-specific logic
* Provides **optional, well-defined extensions** for Node.js

This design adheres to:

* Interface Segregation Principle
* Separation of Concerns
* Reusability best practices

and enables seamless usage across Node.js, browser, CLI, and API contexts.
