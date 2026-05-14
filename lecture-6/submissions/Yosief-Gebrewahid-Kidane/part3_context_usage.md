# Part 3 – Task 3.1
# Usage of Redesigned pdf-parse API in Multiple Contexts

## 1. Objective

Demonstrate how the redesigned **pdf-parse** interfaces (`IPDFSource`, `IPDFParser`, `IPDFExtractor`) can be used across multiple platforms: Node.js, browser, CLI, and API client.  


---

## 2. Node.js Server Example

### Description
Parse a PDF from a URL and extract text.

### Code Example

```ts
import { URLSource, PDFParser, TextExtractor } from "pdf-parse-core"

async function extractTextFromPDF(url: string) {
    // 1. Create a PDF source (URL)
    const source = new URLSource(url)

    // 2. Open parser session
    const parser = new PDFParser()
    const session = await parser.open(source)

    // 3. Get text extractor
    const textExtractor = session.getExtractor<string>("text") as TextExtractor

    // 4. Extract text
    const text = await textExtractor.extract()

    // 5. Close session
    await session.close()

    return text
}

// Usage
extractTextFromPDF("https://example.com/sample.pdf").then(console.log)
```

### Notes
- Same core interfaces (`IPDFSource`, `IPDFParser`, `IPDFExtractor`) as other platforms.
- Node.js loader handles network requests and file system access.
- No Node-specific methods are exposed in the core extractor.

---

## 3. Browser Example

### Description
Parse a PDF from a file input and render the first page as an image.

### Code Example

```ts
import { FileSource, PDFParser, ScreenshotExtractor } from "pdf-parse-core"

async function renderFirstPage(file: File) {
    // 1. Create a PDF source from browser File object
    const source = new FileSource(file)

    // 2. Open parser session
    const parser = new PDFParser()
    const session = await parser.open(source)

    // 3. Get screenshot extractor
    const screenshotExtractor = session.getExtractor<Blob>("screenshot") as ScreenshotExtractor

    // 4. Extract first page screenshot
    const screenshot = await screenshotExtractor.extract({ pages: [1] })

    // 5. Close session
    await session.close()

    return screenshot
}

// Example: file input handler
document.getElementById("fileInput").addEventListener("change", async (e) => {
    const file = (e.target as HTMLInputElement).files[0]
    const firstPageImage = await renderFirstPage(file)
    document.getElementById("preview").src = URL.createObjectURL(firstPageImage)
})
```

### Notes
- Core interface remains the same; only `FileSource` replaces `URLSource`.
- Browser-specific loader abstracts file reading using `FileReader` or `ArrayBuffer`.
- No Node-only features (like `getHeader`) are included.

---

## 4. CLI Example

### Description
Parse a local PDF file and extract text via a CLI command.

### Code Example (Node.js CLI)

```ts
#!/usr/bin/env node
import { BufferSource, PDFParser, TextExtractor } from "pdf-parse-core"
import fs from "fs"

async function main() {
    const filePath = process.argv[2]
    if (!filePath) {
        console.error("Usage: pdf-parse extract-text <file.pdf>")
        process.exit(1)
    }

    const buffer = fs.readFileSync(filePath)
    const source = new BufferSource(buffer)

    const parser = new PDFParser()
    const session = await parser.open(source)
    const textExtractor = session.getExtractor<string>("text") as TextExtractor
    const text = await textExtractor.extract()
    await session.close()

    console.log(text)
}

main()
```

### Notes
- CLI uses `BufferSource` to read local files.
- Core interfaces remain unchanged.
- Supports piping output to other CLI tools or scripts.

---

## 5. API Client 

### Description
Consume the REST API we designed in Part 2 to extract text.

### Code Example

```ts
async function extractTextFromAPI(file: File) {
    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch("/api/v1/extract/text", {
        method: "POST",
        body: formData
    })

    const data = await response.json()
    return data.text
}
```

### Notes
- Same **conceptual interface** (`extractText`) is used, but via HTTP instead of direct library calls.
- Abstracts platform differences behind API endpoints.

---

## 6. Summary of Reusability Across Contexts

| Context | Source Loader | Extractor | Platform-Specific Differences |
|---------|---------------|-----------|-------------------------------|
| Node.js Server | URLSource | TextExtractor | Can use HTTP or file system |
| Browser | FileSource | ScreenshotExtractor | Uses FileReader / ArrayBuffer |
| CLI | BufferSource | TextExtractor | Reads from local file system |
| API Client | API endpoint | Implicit extractor | Uses HTTP request |

