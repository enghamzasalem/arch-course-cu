# Part 1 – Task 1.2: Redesigned Interface Proposal

## Overview

This document proposes a **modular, interface-driven redesign** of the pdf-parse library to improve reusability, extensibility, and cross-platform compatibility.

The redesign separates the system into three core concerns:

1. **Data Source Layer** – Responsible for loading PDF data
2. **Parser Session Layer** – Responsible for managing parsing lifecycle
3. **Extraction Layer** – Responsible for extracting specific content (text, images, tables, etc.)

---

## 1. Proposed Architecture

### 1.1 Layered Design

```
[ IPDFSource ] --> [ IPDFParser / PDFSession ] --> [ IPDFExtractor<T> ]
```

* **IPDFSource** → abstracts input (URL, Buffer, base64)
* **PDFSession** → represents a parsed PDF instance
* **IPDFExtractor<T>** → defines extraction operations

This separation ensures **low coupling and high cohesion**.

---

## 2. Interface Definitions

### 2.1 IPDFSource (Data Loading Abstraction)

```ts
interface IPDFSource {
  load(): Promise<ArrayBuffer>;
  getType(): 'url' | 'buffer' | 'base64';
}
```

#### Implementations

* `URLSource`
* `BufferSource`
* `Base64Source`

#### Contracts

* **Preconditions:**

  * Valid input provided (reachable URL, valid buffer/base64)
* **Postconditions:**

  * Returns PDF data as ArrayBuffer
* **Failure cases:**

  * Network errors, invalid encoding

#### Rationale

* Decouples input handling from parsing
* Enables adding new sources (e.g., stream, file system)

---

### 2.2 IPDFParser / PDFSession (Parsing Layer)

```ts
interface IPDFParser {
  createSession(source: IPDFSource, options?: ParserOptions): Promise<IPDFSession>;
}

interface IPDFSession {
  getMetadata(): Promise<PDFMetadata>;
  destroy(): Promise<void>;
}
```

#### Contracts

* **Preconditions:**

  * Source must be valid and loadable
* **Postconditions:**

  * Returns a session bound to a parsed PDF
* **Lifecycle:**

  * `destroy()` must release resources

#### Rationale

* Introduces explicit lifecycle management
* Encapsulates parsing state
* Enables multiple sessions for different PDFs

---

### 2.3 IPDFExtractor<T> (Extraction Abstraction)

```ts
interface IPDFExtractor<T, P = any> {
  extract(session: IPDFSession, params?: P): Promise<T>;
}
```

#### Example Implementations

```ts
class TextExtractor implements IPDFExtractor<string> {}
class ImageExtractor implements IPDFExtractor<Image[]> {}
class TableExtractor implements IPDFExtractor<Table[]> {}
class ScreenshotExtractor implements IPDFExtractor<Buffer> {}
class InfoExtractor implements IPDFExtractor<PDFMetadata> {}
```

#### Contracts

* **Preconditions:**

  * Valid session
* **Postconditions:**

  * Returns data of type T
* **Error cases:**

  * Unsupported content, parsing errors

#### Rationale

* Standardizes extraction pattern
* Enables pluggable extractors
* Improves extensibility (e.g., `LinkExtractor`)

---

## 3. Alternative Unified Extraction Interface

Optional simplified interface:

```ts
interface IPDFExtractionService {
  extract<T>(type: 'text' | 'image' | 'table' | 'info' | 'screenshot', params?: any): Promise<T>;
}
```

### Trade-off

* ✔ Simpler API for consumers
* ✖ Less type safety and extensibility

---

## 4. Platform Support Design

### 4.1 Core Module (Platform Independent)

* Contains:

  * IPDFSource
    n  - IPDFParser
  * IPDFSession
  * Extractors
* Works in:

  * Node.js
  * Browser

### 4.2 Node-Specific Module

```ts
interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<HeaderInfo>;
}
```

* Exported via: `pdf-parse/node`
* Keeps Node-only logic isolated

### 4.3 Benefits

* Browser users never import Node code
* Clear separation of platform capabilities

---

## 5. Swappable Implementations

### Example: Screenshot Rendering

```ts
interface IScreenshotRenderer {
  render(session: IPDFSession, params?: ScreenshotParams): Promise<Buffer>;
}
```

Possible implementations:

* Canvas-based (browser)
* Headless Chromium (Node)

### Benefit

* Allows runtime swapping without changing API

---

## 6. Reduced Coupling Strategy

| Concern    | Old Design   | New Design           |
| ---------- | ------------ | -------------------- |
| Loading    | Inside class | IPDFSource           |
| Parsing    | Inside class | IPDFParser + Session |
| Extraction | Methods      | Extractor interfaces |
| Platform   | Mixed        | Separate modules     |

---

## 7. Example Usage (Redesigned API)

```ts
const source = new URLSource("https://example.com/sample.pdf");
const parser = new PDFParser();

const session = await parser.createSession(source);

const textExtractor = new TextExtractor();
const text = await textExtractor.extract(session);

await session.destroy();
```

---

## 8. Benefits of the Redesign

### 8.1 Improved Reusability

* Each component reusable independently
* Clear boundaries between layers

### 8.2 Extensibility

* New extractors can be added without modifying core
* Supports plugin architecture

### 8.3 Testability

* Each interface can be mocked independently

### 8.4 Maintainability

* Smaller, focused components
* Easier debugging and upgrades

---

## 9. Conclusion

The redesigned architecture transforms pdf-parse from a **monolithic class-based API** into a **modular, interface-driven system**.

Key improvements:

* Separation of concerns
* Clear contracts
* Platform abstraction
* Pluggable extraction model

This design significantly enhances reuse across:

* Node.js services
* Browser applications
* CLI tools
* REST API layers

---