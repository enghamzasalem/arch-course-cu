# Part 1.2 – Redesigned Interface Proposal for pdf-parse

## Overview

The current **pdf-parse API** centers around a single class (`PDFParse`) that performs multiple responsibilities:

* Loading PDF data
* Managing parsing sessions
* Extracting content (text, images, metadata, tables)
* Rendering screenshots
* Platform-specific operations (e.g., `getHeader` in Node.js)

This monolithic structure increases coupling and reduces flexibility.
To improve **reusability, modularity, and extensibility**, the API can be redesigned into **three main architectural layers**:

1. **Data Source Layer** – Responsible for loading PDF data.
2. **Parser / Session Layer** – Manages the lifecycle of a parsed document.
3. **Extraction Layer** – Performs content extraction operations.

This separation allows components to evolve independently and supports multiple runtime environments.

---

# Proposed Modular Architecture

```
Application
     │
     ▼
PDFParser / Session
     │
     ├── TextExtractor
     ├── ImageExtractor
     ├── TableExtractor
     ├── MetadataExtractor
     └── ScreenshotRenderer
     │
     ▼
IPDFSource (URL, Buffer, Base64)
```

### Responsibilities

| Layer                   | Responsibility                         |
| ----------------------- | -------------------------------------- |
| **IPDFSource**          | Defines how PDF data is loaded         |
| **PDFSession / Parser** | Maintains parsed document state        |
| **Extractors**          | Perform specific extraction operations |

This architecture reduces coupling between data loading, parsing, and extraction logic.

---

# Interface 1: IPDFSource

The **IPDFSource** interface abstracts how PDF data is obtained.

### Purpose

Provide a unified interface for loading PDF data regardless of where it originates.

### Example Implementations

* `URLPDFSource`
* `BufferPDFSource`
* `Base64PDFSource`
* `FilePDFSource`

---

## Interface Definition (TypeScript-style pseudocode)

```ts
interface IPDFSource {
    load(): Promise<PDFBinaryData>
}
```

### Example Implementations

```ts
class URLPDFSource implements IPDFSource {
    constructor(url: string)
    load(): Promise<PDFBinaryData>
}

class BufferPDFSource implements IPDFSource {
    constructor(buffer: Buffer)
    load(): Promise<PDFBinaryData>
}
```

---

## Contract

### Preconditions

* The source must provide valid PDF binary data.
* Network sources must provide a reachable URL.

### Postconditions

* `load()` returns binary PDF data ready for parsing.
* Errors are raised if the data cannot be retrieved.

---

## Rationale

Separating data sources allows:

* New sources to be added without changing parser logic
* Reuse of parsing logic across environments
* Simplified testing with mock sources

Example:

```
parser = PDFParser(new URLPDFSource(url))
```

The parser does not need to know how the PDF was obtained.

---

# Interface 2: IPDFParser / PDFSession

The **parser session** represents a parsed PDF document.

### Responsibilities

* Initialize parsing
* Maintain document state
* Provide access to extractors

---

## Interface Definition

```ts
interface IPDFParser {
    open(source: IPDFSource): Promise<PDFSession>
}
```

### Session Object

```ts
interface PDFSession {
    extract<T>(extractor: IExtractor<T>, params?: ExtractParams): Promise<T>
    close(): void
}
```

---

## Contract

### Preconditions

* A valid `IPDFSource` must be provided.
* Source must contain valid PDF data.

### Postconditions

* A `PDFSession` object is returned.
* The session remains valid until `close()` is called.

---

## Rationale

Separating parsing sessions:

* Avoids repeated parsing for each operation
* Allows multiple extraction operations on the same document
* Supports session lifecycle management

Example usage:

```ts
source = new URLPDFSource(url)
parser = new PDFParser()

session = await parser.open(source)

text = await session.extract(new TextExtractor())
info = await session.extract(new MetadataExtractor())

session.close()
```

---

# Interface 3: IExtractor<T>

Extraction operations follow a **common pattern**.

Examples:

* Text extraction
* Image extraction
* Table extraction
* Metadata extraction

These operations can implement a shared interface.

---

## Interface Definition

```ts
interface IExtractor<T> {
    extract(session: PDFSession, params?: ExtractParams): Promise<T>
}
```

---

## Example Implementations

### Text Extraction

```ts
class TextExtractor implements IExtractor<string> {
    extract(session: PDFSession): Promise<string>
}
```

### Image Extraction

```ts
class ImageExtractor implements IExtractor<Image[]> {
    extract(session: PDFSession, params?: ImageOptions): Promise<Image[]>
}
```

### Table Extraction

```ts
class TableExtractor implements IExtractor<Table[]> {
    extract(session: PDFSession): Promise<Table[]>
}
```

### Screenshot Renderer

```ts
class ScreenshotExtractor implements IExtractor<Image> {
    extract(session: PDFSession, params?: ScreenshotOptions): Promise<Image>
}
```

---

## Contract

### Preconditions

* A valid `PDFSession` must exist.
* Extraction parameters must match the extractor type.

### Postconditions

* Returns extracted content of type `T`.
* Does not modify the underlying PDF document.

---

# Node.js vs Browser Support

Platform-specific features should be implemented as **optional modules**.

### Example

```
core/
  parser
  extractors
  sources

node/
  NodeHeaderExtractor

browser/
  BrowserRenderer
```

Example Node-specific extractor:

```ts
class NodeHeaderExtractor implements IExtractor<HeaderInfo> {
    extract(session: PDFSession): Promise<HeaderInfo>
}
```

This prevents browser environments from exposing unsupported APIs.

---

# Swappable Implementations

The modular architecture allows components to be replaced.

Example: screenshot rendering engines

```
ScreenshotExtractor
   ├── CanvasRenderer
   ├── WebGLRenderer
   └── NodePDFRenderer
```

Applications can choose the implementation:

```ts
renderer = new CanvasRenderer()
session.extract(new ScreenshotExtractor(renderer))
```

Benefits:

* Performance tuning
* Environment-specific optimizations
* Plugin ecosystem

---

# Coupling Reduction

The new architecture reduces coupling by separating responsibilities.

| Concern            | Component    |
| ------------------ | ------------ |
| Data loading       | `IPDFSource` |
| Parsing            | `PDFParser`  |
| Document lifecycle | `PDFSession` |
| Content extraction | `IExtractor` |

Previously, all of these responsibilities were inside a single class.

Benefits include:

* Easier testing
* Better maintainability
* Clear separation of concerns
* Independent evolution of components

---

# Example Usage

```
source = URLPDFSource("invoice.pdf")

parser = PDFParser()

session = parser.open(source)

text = session.extract(TextExtractor())
tables = session.extract(TableExtractor())

session.close()
```

---

# Benefits of the Proposed Design

### Improved Reusability

Components can be reused independently across systems.

### Better Modularity

Each component has a single responsibility.

### Cross-Platform Compatibility

Platform-specific features are isolated in modules.

### Extensibility

New extractors and data sources can be added without modifying core interfaces.

---

# Conclusion

The redesigned interface architecture improves the original pdf-parse API by:

* Separating data loading, parsing, and extraction responsibilities
* Defining clear contracts and reusable interfaces
* Supporting multiple platforms without polluting the core API
* Allowing new extraction operations and implementations to be added easily

This modular architecture aligns with principles of **encapsulation, interface stability, and reusable component design**.
