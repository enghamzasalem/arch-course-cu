# Part 4.1 – v1 → v2 Migration and Future Evolution

## Overview

The **pdf-parse** library evolved from a simple functional API (v1) to a class-based API (v2).  
This evolution improves **reusability, configurability, and lifecycle management**, making the library easier to integrate across multiple environments such as Node.js, browsers, serverless functions, and REST services.

This document describes:

1. How the **v1 API can be deprecated cleanly**
2. What **v2 improves for reusability**
3. A **future evolution proposal (v2.5 / v3)** while maintaining backward compatibility
4. Migration guidance for developers

---

# v1 API Design

The original API was a **single function**.

Example usage:

pdf(buffer).then(result => {
    console.log(result.text)
})

Characteristics of v1
| Property      | Description                    |
| ------------- | ------------------------------ |
| Interface     | Single function                |
| Input         | Buffer                         |
| Output        | Promise with text and metadata |
| Lifecycle     | None                           |
| Configuration | Limited                        |


Limitations

- No instance lifecycle
- Limited extensibility
- Hard to support multiple operations
- Difficult to manage resources

Example limitations:

- No cleanup mechanism
- No reusable parsing session
- Difficult to add features like screenshots or image extraction

# v2 API Design

Version 2 introduced a class-based API.

Example usage:
const parser = new PDFParse({ data: buffer })
const text = await parser.getText()
parser.destroy()

Key Improvements
| Feature              | Improvement                             |
| -------------------- | --------------------------------------- |
| Instance lifecycle   | Parser instance manages state           |
| Multiple operations  | Same document used for many extractions |
| Resource cleanup     | `destroy()` frees memory                |
| Configurable options | Worker configuration possible           |
| Cross-platform       | Works in Node and browser               |

## Why v2 Improves Reusability
### 1. Instance Lifecycle

The parser instance represents a document session.

Example:

const parser = new PDFParse({ data: buffer })
await parser.getText()
await parser.getInfo()
await parser.getImage()
parser.destroy()

Benefits:

- The PDF is parsed only once
- Multiple operations reuse the same session
- Improves performance

### 2. Configurable Worker

Large PDFs may require background processing.

Example:

const parser = new PDFParse({
    data: buffer,
    workerPath: "/pdf.worker.js"
})

Benefits:

- Supports browser workers
- Enables parallel processing
- Improves scalability

### 3. Clear API Surface

The class exposes explicit methods:

getText()
getInfo()
getImage()
getTable()
getScreenshot()
destroy()

This improves discoverability and API clarity.

# Deprecating v1 Cleanly

A clean migration strategy avoids breaking existing users immediately.

## Step 1 – Introduce Deprecation Warning

When the v1 function is used:

function pdf(data) {
    console.warn(
        "pdf() is deprecated. Use new PDFParse({ data }) instead."
    )
    const parser = new PDFParse({ data })
    return parser.getText()
}

Users receive a warning but their code still works.

## Step 2 – Provide Migration Guide

Documentation should include clear migration instructions.

Migration Example

v1:
pdf(buffer).then(r => console.log(r.text))

v2:
const parser = new PDFParse({ data: buffer })
const text = await parser.getText()
parser.destroy()


## Step 3 – Deprecation Timeline
| Version | Change                     |
| ------- | -------------------------- |
| v2.0    | v1 API marked deprecated   |
| v2.x    | Deprecation warnings shown |
| v3.0    | v1 API removed             |

This allows users sufficient time to migrate.

# Future Evolution Proposal
## Proposal: Streaming Text Extraction

Large PDF files can produce extremely large text outputs.

A new optional feature could allow stream-based text extraction.

## Proposed Method
getTextStream(options?)

Example:

const parser = new PDFParse({ data: buffer })

const stream = parser.getTextStream()

stream.on("data", chunk => {
    console.log(chunk)
})
Benefits
| Benefit             | Description                         |
| ------------------- | ----------------------------------- |
| Memory efficiency   | Avoid loading entire text in memory |
| Scalability         | Better for large PDFs               |
| Streaming pipelines | Works with Node streams             |
