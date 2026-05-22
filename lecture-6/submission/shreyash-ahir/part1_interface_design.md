# Part 1.2 — Redesigned Interface Proposal

## Design Rationale

The redesign separates three concerns that the current API conflates:

1. **Source Loading** — how a PDF is obtained (URL, Buffer, base64)
2. **Parser Session** — a stateful session around a loaded PDF
3. **Extraction** — pulling specific content out of the session

Each concern has its own interface.  A caller that only needs text extraction
depends only on `IPDFExtractor`, not on loading or session internals.

This applies the principle from the course: *"Every component communicates
with as few others as possible"* (Few Interfaces Principle), and *"maximize
information hiding"* (Design Advice, Joshua Bloch).

---

## Interface 1: IPDFSource

**Purpose:** Describe how a PDF is loaded, without coupling callers to a
specific loading mechanism (HTTP, filesystem, in-memory buffer).

```typescript
/** Describes a single PDF input source. Immutable value object. */
interface IPDFSource {
  /** Returns the raw PDF bytes, resolved asynchronously. */
  load(): Promise<Uint8Array>;
}

// Concrete implementations (not part of the interface contract):

/** Load from a URL (works in Node and browser) */
class URLSource implements IPDFSource {
  constructor(
    private readonly url: string,
    private readonly options?: { password?: string; headers?: Record<string,string> }
  ) {}
  async load(): Promise<Uint8Array> { /* fetch + decrypt */ }
}

/** Load from an in-memory buffer or base64 string */
class BufferSource implements IPDFSource {
  constructor(
    private readonly data: Uint8Array | string, // string = base64
    private readonly options?: { password?: string }
  ) {}
  async load(): Promise<Uint8Array> { /* decode + decrypt */ }
}
```

**Contract for `load()`:**
- Pre-condition: `url` is a valid absolute URL, or `data` is a non-empty
  buffer or valid base64 string.
- Post-condition: Returns the raw bytes of a valid PDF file.
- Error: Throws `PDFLoadError` if the source cannot be reached, the content
  is not a PDF, or the password is wrong.

**Rationale:**  
Loading a PDF is a separate concern from parsing it.  A browser-based caller
uses `URLSource` with a relative URL; a Node.js server uses `BufferSource`
after reading from disk.  The parser session never cares how the bytes arrived.

---

## Interface 2: IPDFSession

**Purpose:** Represent a parsed, ready-to-query PDF.  Lifecycle is explicit:
open → use → close.

```typescript
interface IPDFSession {
  /** Number of pages in the document. Available after open(). */
  readonly pageCount: number;

  /** Open and parse the PDF from the given source. */
  open(source: IPDFSource): Promise<void>;

  /** Release all resources (workers, memory). Must be called when done. */
  close(): Promise<void>;
}
```

**Contract for `open(source)`:**
- Pre-condition: `source.load()` resolves successfully; session is not
  already open.
- Post-condition: Internal state is populated; `pageCount` is accurate;
  all extractors bound to this session are ready.
- Error: Throws `PDFParseError` if the PDF is malformed or encrypted.

**Contract for `close()`:**
- Pre-condition: session was previously opened.
- Post-condition: All workers/memory are released.  Any subsequent call to
  an extractor on this session throws `SessionClosedError`.

---

## Interface 3: IPDFExtractor\<T\>

**Purpose:** A uniform contract for all extraction operations.  Using a
generic parameter `T` avoids a separate method per content type while still
being strongly typed.

```typescript
interface IPDFExtractor<T> {
  /**
   * Extract content of type T from the session.
   * @param session  An open IPDFSession.
   * @param options  Extraction-specific parameters (page range, scale, etc.)
   */
  extract(session: IPDFSession, options?: ExtractOptions): Promise<T>;
}

/** Options shared across extractors */
interface ExtractOptions {
  pages?: number[];          // which pages (default: all)
  [key: string]: unknown;    // extractor-specific keys
}

// Concrete extractor return types:
interface TextResult    { pages: { pageNumber: number; text: string }[] }
interface InfoResult    { title?: string; author?: string; pageCount: number; [key: string]: unknown }
interface ImageResult   { images: { pageNumber: number; data: Uint8Array; mimeType: string }[] }
interface TableResult   { tables: { pageNumber: number; rows: string[][] }[] }
interface ScreenshotResult { screenshots: { pageNumber: number; data: Uint8Array; width: number; height: number }[] }

// Concrete implementations:
class TextExtractor     implements IPDFExtractor<TextResult>      { ... }
class InfoExtractor     implements IPDFExtractor<InfoResult>       { ... }
class ImageExtractor    implements IPDFExtractor<ImageResult>      { ... }
class TableExtractor    implements IPDFExtractor<TableResult>      { ... }
class ScreenshotExtractor implements IPDFExtractor<ScreenshotResult> { ... }
```

**Contract for `extract(session, options)`:**
- Pre-condition: `session` is open (not closed); `options.pages` (if provided)
  contains only valid page numbers within [1, session.pageCount].
- Post-condition: Returns extracted content for the requested pages in
  document order.
- Error: Throws `ExtractionError` on internal parse failure.
  Throws `SessionClosedError` if session is already closed.

**Why a generic interface instead of separate methods?**  
Adding a new extraction type (e.g. `LinkExtractor`) requires only a new
class that implements `IPDFExtractor<LinkResult>`.  No existing interface
changes; no existing clients break.  This is "easier to add than to remove"
from the course evolution advice applied at design time.

---

## How the Design Supports Node.js and Browser

```
Core (shared):  IPDFSource, IPDFSession, IPDFExtractor<T>
                URLSource, BufferSource
                TextExtractor, InfoExtractor, ImageExtractor,
                TableExtractor, ScreenshotExtractor

Node extras:    INodePDFUtils (getHeader)
                NodeURLSource (can use http.request with Range header)
```

A browser caller never imports `INodePDFUtils`.  A Node caller opts in by
importing from `pdf-parse/node`.  The core interfaces are identical in both
environments.

---

## How Implementations Can Be Swapped

Because `IPDFSession` and `IPDFExtractor<T>` are interfaces, a caller can
inject a different renderer for screenshots (e.g. a canvas-based renderer in
the browser vs. a headless renderer in Node) without changing any calling code.

```typescript
// Node.js — use headless renderer
const session = new PDFSession({ renderer: new HeadlessRenderer() });

// Browser — use canvas renderer
const session = new PDFSession({ renderer: new CanvasRenderer() });

// Caller code is identical in both cases:
const extractor = new ScreenshotExtractor();
const result = await extractor.extract(session, { pages: [1] });
```

---

## Coupling Reduction

| Old design | New design |
|---|---|
| Caller depends on full `PDFParse` class | Caller depends only on `IPDFExtractor<T>` |
| Source type coupled to parser constructor | `IPDFSource` is a separate injectable |
| Platform-specific `getHeader` in core | `INodePDFUtils` in `pdf-parse/node` only |
| Rendering config mixed with source config | Session options separate from source options |
