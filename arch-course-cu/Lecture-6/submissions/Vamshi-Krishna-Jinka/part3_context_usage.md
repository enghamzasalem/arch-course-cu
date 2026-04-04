# Part 3.1 – Usage in Multiple Contexts

## Overview

The redesigned API separates responsibilities into reusable interfaces:

- **IPDFSource** – how the PDF is loaded  
- **IPDFParser / PDFSession** – parsing lifecycle  
- **IExtractor<T>** – extraction operations (text, images, tables, etc.)

Because these interfaces are **platform-independent**, the same API can be used in:

- Node.js servers
- Browser applications
- CLI tools
- External clients through a REST API

Only the **construction or configuration** of the source or environment changes.  
The **core interface remains the same**, which improves portability and reuse.

---

# Core Interface (Shared Across Contexts)

The following pseudocode represents the core API used in every environment.

```typescript
interface IPDFSource {
    load(): Promise<PDFBinaryData>
}

interface IPDFParser {
    open(source: IPDFSource): Promise<PDFSession>
}

interface PDFSession {
    extract<T>(extractor: IExtractor<T>, params?): Promise<T>
    close(): void
}

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

All contexts use this same interface.


# Context 1: Node.js Server

## Scenario

A Node.js backend service receives a PDF URL and extracts text from the document.

## Example Code
import { PDFParser, URLSource, TextExtractor } from "pdf-parse-api"

async function extractTextFromURL(url) {

    const source = new URLSource(url)

    const parser = new PDFParser()

    const session = await parser.open(source)

    const text = await session.extract(new TextExtractor())

    session.close()

    return text
}

What is Platform-Specific
| Element      | Purpose                                |
| ------------ | -------------------------------------- |
| URLSource    | Loads PDF from network                 |
| Node runtime | Handles networking and file operations |

What is Shared

- PDFParser
- PDFSession
- TextExtractor

These components are identical across environments.

# Context 2: Browser Application

## Scenario

A user uploads a PDF in a browser and the application renders the first page.

## Example Code
import { PDFParser, FileSource, ScreenshotExtractor } from "pdf-parse-api"

async function previewPDF(file) {

    const source = new FileSource(file)

    const parser = new PDFParser()

    const session = await parser.open(source)

    const image = await session.extract(
        new ScreenshotExtractor({ page: 1, scale: 2 })
    )

    session.close()

    displayImage(image)
}

What is Platform-Specific
| Element        | Purpose                       |
| -------------- | ----------------------------- |
| FileSource     | Reads file from browser input |
| CanvasRenderer | Used internally for rendering |

What is Shared

- PDFParser
- PDFSession
- ScreenshotExtractor

The browser environment only changes how the PDF is loaded.

# Context 3: CLI Tool

## Scenario

A command-line tool extracts text from a local PDF file.

Example command:
pdf-parse extract-text input.pdf

## Example Implementation
import { PDFParser, FileSource, TextExtractor } from "pdf-parse-api"

async function runCLI(inputPath) {

    const source = new FileSource(inputPath)

    const parser = new PDFParser()

    const session = await parser.open(source)

    const text = await session.extract(new TextExtractor())

    session.close()

    console.log(text)
}

What is Platform-Specific
| Element              | Purpose                   |
| -------------------- | ------------------------- |
| FileSource           | Loads local file          |
| CLI argument parsing | Provided by CLI framework |

What is Shared

The core extraction logic remains identical to the Node.js example.


# Context 4: REST API Client

## Scenario

An external application calls the REST API wrapper created in Task 2.

## Example Request
POST /api/v1/extract/text

Request body:

{
  "url": "https://example.com/report.pdf"
}


## Example Client Code
async function extractTextViaAPI(url) {

    const response = await fetch("/api/v1/extract/text", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url })
    })

    const data = await response.json()

    return data.text
}

## Internal API Processing

Inside the API service:

Client → REST API → PDFParser → Extractor → Response

The REST service simply wraps the same core library interface.