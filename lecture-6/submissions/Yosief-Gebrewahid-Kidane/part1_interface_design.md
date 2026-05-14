# Part 1 – Task 1.2  
# Redesigned Interface Proposal for pdf-parse

## 1. Objective

Improving the **reusability, modularity, and maintainability** of the pdf-parse library by introducing a clearer interface architecture.

The current API relies on a **single class (`PDFParse`)** that performs many responsibilities.

The redesigned architecture separates these responsibilities into **independent components** with clearly defined interfaces.

---

# 2. Proposed Modular Architecture

The redesigned system separates functionality into three layers:

```
PDF Source → Parser Session → Extractors
```

| Component | Responsibility |
|-----------|---------------|
| **IPDFSource** | Defines how a PDF document is loaded |
| **IPDFParser** | Creates and manages a parsing session |
| **IPDFExtractor** | Extracts specific content from the PDF |



---

# 3. Interface 1 – IPDFSource



The `IPDFSource` interface abstracts how a PDF document is loaded.  
Instead of embedding file loading logic inside the parser, different implementations can provide different input sources.

Supported sources:

- URL
- Buffer
- Base64 string
- File upload

---

## Interface Definition

```ts
interface IPDFSource {
  load(): Promise<ArrayBuffer>
}
```

---

## Implementations

### URL Source

```ts
class URLSource implements IPDFSource {
  constructor(private url: string) {}

  async load(): Promise<ArrayBuffer> {
    const response = await fetch(this.url)
    return await response.arrayBuffer()
  }
}
```

### Buffer Source

```ts
class BufferSource implements IPDFSource {
  constructor(private buffer: Buffer) {}

  async load(): Promise<ArrayBuffer> {
    return this.buffer
  }
}
```

### Base64 Source

```ts
class Base64Source implements IPDFSource {
  constructor(private base64: string) {}

  async load(): Promise<ArrayBuffer> {
    return decodeBase64(this.base64)
  }
}
```

---

## Interface Contract

### Preconditions

- A valid PDF source must be provided.
- The source must contain a valid PDF document.

### Postconditions

- The `load()` method returns the PDF as binary data (`ArrayBuffer`).

### Possible Errors

- Network failure when loading from URL
- Invalid or corrupted PDF content

---

## Rationale

Separating the source loading logic from the parser allows the system to support **multiple input formats without modifying the parsing code**. 

---

# 4. Interface 2 – IPDFParser



The `IPDFParser` interface manages the **parsing lifecycle**.  
It is responsible for creating a parsing session from a given PDF source.

---

## Interface Definition

```ts
interface IPDFParser {
  open(source: IPDFSource): Promise<PDFSession>
}
```

---

## PDFSession Interface

A `PDFSession` represents a parsed document.

```ts
interface PDFSession {
  getExtractor<T>(type: string): IPDFExtractor<T>
  close(): Promise<void>
}
```

---

## Example

```ts
const source = new URLSource("file.pdf")

const parser = new PDFParser()

const session = await parser.open(source)
```

---

## Interface Contract

### Preconditions

- A valid `IPDFSource` instance must be provided.

### Postconditions

- A `PDFSession` object is returned representing the parsed document.

### Possible Errors

- Unsupported PDF format
- Encrypted PDF without password

---

## Rationale

Separating parsing from extraction ensures that the **document is parsed once and reused by multiple extractors**.

---

# 5. Interface 3 – IPDFExtractor



The `IPDFExtractor` interface defines how specific information is extracted from a parsed PDF document.

Each extractor is responsible for one type of output.


- text extraction
- image extraction
- table extraction
- screenshot rendering
- metadata extraction

---

## Interface Definition

```ts
interface IPDFExtractor<T> {
  extract(params?: any): Promise<T>
}
```

---

## Extractors

### Text Extractor

```ts
class TextExtractor implements IPDFExtractor<string> {
  async extract(): Promise<string> {
    // text extraction logic
  }
}
```

### Image Extractor

```ts
class ImageExtractor implements IPDFExtractor<Image[]> {
  async extract(): Promise<Image[]> {
    // image extraction logic
  }
}
```

### Table Extractor

```ts
class TableExtractor implements IPDFExtractor<Table[]> {
  async extract(): Promise<Table[]> {
    // table extraction logic
  }
}
```

---

## Rationale

By separating extraction logic into independent extractors, the system becomes easier to extend.

---

# 6. Supporting Node.js and Browser 

The redesigned architecture supports multiple platforms by separating platform-specific modules.

Example package structure:

```
pdf-parse/
 ├ core/
 │  ├ IPDFSource.ts
 │  ├ IPDFParser.ts
 │  ├ IPDFExtractor.ts
 │
 ├ node/
 │  └ HeaderReader.ts
 │
 └ browser/
    └ WorkerLoader.ts
```

**Core module**

- Contains platform-independent interfaces.
- Works in both Node.js and browser environments.

**Node module**

- Contains Node-specific features such as `getHeader()`.

**Browser module**

- Contains browser-specific configurations such as worker initialization.

This separation ensures browser users do not depend on Node.js code.

---

# 7. Swappable Implementations

The interface-based design allows components to be replaced easily.

Examples:

| Component | Possible Implementations |
|-----------|--------------------------|
| Source | URLSource, BufferSource, Base64Source |
| Parser | PDFJSParser, CustomParser |
| Screenshot extractor | CanvasRenderer, WebGLRenderer |


---

# 8. Reduced Coupling

The redesigned architecture reduces coupling by separating responsibilities:

| Responsibility | Component |
|---------------|-----------|
| Loading documents | IPDFSource |
| Parsing documents | IPDFParser |
| Extracting content | IPDFExtractor |

Each component interacts through **interfaces rather than concrete implementations**, making the system easier to maintain and extend.



