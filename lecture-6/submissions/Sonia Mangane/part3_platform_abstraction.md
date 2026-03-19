## Part 3.2: Platform Abstraction (Node vs. Browser)

This section explains how I handled platform differences between **Node.js** and the **Browser** without breaking reusability.

---

## 1. The Problem: “Platform Leakage”

When building a cross-platform library, we often run into features that are only possible (or only practical) in one environment.

Example:
- In **Node.js**, we can do **HTTP Range Requests** to read just part of a PDF (like the header) without downloading the entire file.
- In the **Browser**, we usually end up downloading the whole PDF into memory as a blob/array buffer.

So if we put a Node-only method like `getHeader()` into the **core** `IPDFParser` interface, the Browser implementation is forced to do something bad:

- **Option A:** Throw a “Not Implemented” error (annoying and confusing for users).
- **Option B:** Bundle Node-specific networking logic into the browser build (bloats bundle size and increases risk).

---

## 2. Chosen Approach: Submodule + Extension Interface

I chose a **hybrid “submodule” approach**:

- **`pdf-parse` (Core):** Contains only the standard methods that work everywhere.
- **`pdf-parse/node` (Extra):** A Node-specific entry point that extends the core parser with Node-only utilities (like `getHeader`).

This keeps the core lightweight and makes Node-only features **opt-in**.

---

## 3. How it Works

### Step A: The core remains “pure”

The core interface only includes what we can guarantee in every environment.

```ts
// pdf-parse/core

export interface IPDFParser {
  getText(source: PDFSource): Promise<string>;
  getInfo(source: PDFSource): Promise<PDFInfo>;
  // ... other universal methods
}
```

### Step B: Node utilities live in a separate interface

We define a separate interface for features that require the Node.js runtime (like `fs` or advanced HTTP behavior).

```ts
// pdf-parse/node

import { IPDFParser } from "../core";

export interface INodePDFUtils {
  /**
   * Performs a partial HTTP range request to get
   * metadata without a full download.
   */
  getHeader(url: string): Promise<PDFHeader>;
}

// A specialized version for Node users
export interface INodePDFParser extends IPDFParser, INodePDFUtils {}
```

---

## 4. Usage: How users “opt-in”

### Browser user (zero bloat)

The browser user only imports from the core. They never see or bundle the `getHeader` logic, keeping the frontend bundle small.

```ts
import { createBrowserParser } from "pdf-parse";

const parser = createBrowserParser();
const text = await parser.getText(source);

// parser.getHeader() does not exist here
```

### Node user (full power)

The Node user explicitly imports the Node entry point. This gives them the standard parser plus the extra utilities.

```ts
import { createNodeParser } from "pdf-parse/node";

const parser = createNodeParser();

// Standard core method
const text = await parser.getText(source);

// Node-specific opt-in method
const header = await parser.getHeader("http://example.com/huge-file.pdf");
```

---

## 5. Why this is the best move

- **Clean bundles:** Tools like Webpack/Vite won’t include Node code in the browser build because it’s behind a different import path (`pdf-parse/node`).
- **Type safety:** If a browser dev tries to call `getHeader()`, TypeScript/IDE will flag it immediately (no runtime surprise).
- **Future proof:** If we add a browser-only feature later, we can create something like `pdf-parse/browser` without confusing Node users or polluting the core interface.
