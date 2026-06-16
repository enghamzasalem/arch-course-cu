# Part 3.2 – Platform Abstraction (Node vs Browser)

## Overview

The redesigned API must support **multiple platforms (Node.js and browsers)** while keeping the **core interface clean and reusable**. Some features, such as `getHeader`, rely on **Node-specific capabilities** (for example HTTP range requests and filesystem/network control). These features should **not appear in the core interface**, because they would break compatibility in browser environments.

To solve this, the architecture separates **platform-independent functionality** from **platform-specific extensions**.

---

# Chosen Approach

The design combines two techniques:

1. **Core module + Node submodule**
2. **Optional capability interface**

This ensures that:

- The **core module works in both Node and browser environments**
- **Node-only functionality is isolated**
- Users explicitly opt into Node-specific features

Module structure:
pdf-parse/
│
├── core
│ ├── parser
│ ├── extractors
│ └── sources
│
├── node
│ ├── NodeHeaderExtractor
│ └── NodeNetworkSource
│
└── browser
├── BrowserFileSource
└── CanvasRenderer


The **core module contains only cross-platform features**.

---

# Core Interface (Cross-Platform)

The core interface supports operations that work in **both Node and browser environments**.

Examples:

- `getText`
- `getInfo`
- `getImage`
- `getTable`
- `getScreenshot`

These are implemented through extractors.

Example interface:

```
interface IExtractor<T> {
    extract(session: PDFSession, params?): Promise<T>
}
```
Example extractors:

- TextExtractor
- ImageExtractor
- TableExtractor
- MetadataExtractor
- ScreenshotExtractor

All of these work with binary PDF data already loaded into memory, so they are independent of platform APIs.

# Node-Specific Capability Interface

Some operations require Node-specific capabilities.

Example:

getHeader()

This method retrieves metadata using HTTP range requests, allowing the header of a PDF to be read without downloading the full file.

This functionality is implemented using a Node-specific capability interface.

Example interface:

interface INodePDFUtils {
    getHeader(url: string): Promise<PDFHeaderInfo>
}

Implementation example:
NodeHeaderExtractor implements INodePDFUtils

This interface exists only in the Node submodule.

# Using the Core Module (Browser)

A browser application imports only the core module.

Example:

import { PDFParser, FileSource, TextExtractor } from "pdf-parse"

Example usage:

const source = new FileSource(file)
const parser = new PDFParser()
const session = await parser.open(source)
const text = await session.extract(new TextExtractor())
session.close()

Browser users:

- Never import Node modules
- Never depend on Node APIs
- Only interact with the core interfaces

This ensures browser compatibility and smaller bundles.

# Using Node Extensions

Node users can optionally import the Node module.

Example:

import { NodeHeaderExtractor } from "pdf-parse/node"

Example usage:

const nodeUtils = new NodeHeaderExtractor()

const header = await nodeUtils.getHeader(
    "https://example.com/document.pdf"
)

console.log(header)

Node users explicitly opt in to the Node-specific functionality.

# Dependency Separation

The architecture ensures the following dependency rules.

Browser App
    ↓
pdf-parse (core)

Node App
    ↓
pdf-parse (core)
    ↓
pdf-parse/node

Important rule:
Core module NEVER depends on Node code

This prevents accidental platform coupling.

# Build and Export Strategy

The package exports different modules.

Example:

pdf-parse
pdf-parse/node
pdf-parse/browser

Example package.json exports configuration:

{
  "exports": {
    ".": "./core/index.js",
    "./node": "./node/index.js",
    "./browser": "./browser/index.js"
  }
}

This ensures:
Browsers import only browser-compatible code
Node applications can access additional utilities