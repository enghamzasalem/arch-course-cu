# Part 1.2 – Redesigned Interface Proposal for pdf-parse

## Modular Design

The redesign separates the system into three distinct layers:

- **Source layer** – how the PDF is obtained (URL, Buffer, base64)
- **Session layer** – an opened document created from a source
- **Extraction layer** – operations that read data from the document

---

## Interface: `IPDFLoader`

Responsible only for acquiring PDF data.

```ts
interface IPDFLoader {
  fetch(): Promise<Uint8Array>;
  getIdentifier(): string;
}
```

**Implementations:**

```ts
class UrlLoader implements IPDFLoader {
  constructor(private url: string, private options?: RequestInit) {}
  
  async fetch(): Promise<Uint8Array> {
    // Fetch PDF from URL
    const response = await fetch(this.url);
    const buffer = await response.arrayBuffer();
    return new Uint8Array(buffer);
  }
  
  getIdentifier(): string {
    return `url:${this.url}`;
  }
}

class BufferLoader implements IPDFLoader {
  constructor(private buffer: Uint8Array) {}
  
  async fetch(): Promise<Uint8Array> {
    return this.buffer;
  }
  
  getIdentifier(): string {
    return `buffer:${this.buffer.length} bytes`;
  }
}

class Base64Loader implements IPDFLoader {
  constructor(private base64: string) {}
  
  async fetch(): Promise<Uint8Array> {
    // Decode base64 to binary
    const binary = atob(this.base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }
  
  getIdentifier(): string {
    return `base64:${this.base64.slice(0, 20)}...`;
  }
}
```

**Contract**

- Preconditions: the source must point to valid PDF content
- Postconditions: `load()` returns binary PDF data ready for the session; the source does not perform parsing or extraction

**Rationale:** Loading a PDF is a different responsibility from parsing it. Separating these concerns allows the same parsing logic to be reused with different input types.

---

## Interface: `IPDFSession`

Represents an opened PDF document and manages its lifecycle.

```ts
interface IPDFSession {
  open(source: IPDFSource): Promise<void>;
  close(): Promise<void>;
  isOpen(): boolean;
}
```

**Contract**

- Preconditions: `open()` requires a valid `IPDFSource`; extractors should only be called after the session is open
- Postconditions: after `open()`, the session is ready for extraction; after `close()`, resources are released

**Rationale:** A separate session interface makes the document lifecycle explicit and allows different extractors to share the same session without coupling them to the loading logic.

---

## Interface: `IPDFExtractor<T>`

All extraction operations follow the same pattern: they accept an open session and return a typed result.

```ts
interface IPDFExtractor<T> {
  extract(session: IPDFSession, options?: ExtractOptions): Promise<T>;
}
```

**Implementations:**

```ts
class TextExtractor       implements IPDFExtractor<TextResult>
class InfoExtractor       implements IPDFExtractor<InfoResult>
class ImageExtractor      implements IPDFExtractor<ImageResult>
class TableExtractor      implements IPDFExtractor<TableResult>
class ScreenshotExtractor implements IPDFExtractor<ScreenshotResult>
```

**Extraction options (grouped by extractor):**

```ts
type ExtractOptions      = { pages?: number[]; firstPage?: number; lastPage?: number };
type ImageExtractOptions = ExtractOptions & { imageThreshold?: number };
type ScreenshotOptions   = ExtractOptions & { scale?: number; targetWidth?: number };
type InfoExtractOptions  = { parsePageInfo?: boolean };
```

**Contract**

- Preconditions: the session must already be open; options must be valid for the specific extractor
- Postconditions: returns a result of type `T`; does not modify the source or session state

**Rationale:** A shared extractor interface removes the need to place all extraction methods inside one large class. New extractors can be added without modifying the session or source interfaces.

---

## Node.js and Browser Support

The shared core works in both environments. The core interfaces do not depend on any Node.js-specific APIs such as the file system or native modules. They only use standard async patterns and binary data types, which are available in both environments. This means the same `IPDFSource`, `IPDFSession`, and `IPDFExtractor<T>` implementations can run in a browser without modification.

- `IPDFSource`, `IPDFSession`, `IPDFExtractor<T>` and all extractor classes are platform-independent

Node-only functionality is placed in a separate module:

```ts
// pdf-parse/node
interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<HeaderResult>;
}
```

A browser user never imports `pdf-parse/node`. A Node.js user can opt in when needed.

---

## Swapping Implementations

Because each part depends on an interface rather than a concrete class, implementations can be replaced independently.

- `ScreenshotExtractor` can be swapped for a browser-safe or Node-optimized renderer — both implement `IPDFExtractor<ScreenshotResult>`
- `UrlPDFSource`, `BufferPDFSource`, and `Base64PDFSource` are interchangeable — the session and extractors do not change

---

## How the Design Reduces Coupling

- The source only provides bytes — it has no knowledge of parsing or extraction
- The session manages document lifecycle — it does not contain extraction logic
- Each extractor has one responsibility — extractors do not depend on each other or on the source type