# Task 1.2 — Redesigned Interface Proposal
## pdf-parse v2.4.5 · Chapter 6: Reusability and Interfaces

---

## 1. Design Rationale

The current `PDFParse` class conflates three orthogonal concerns into a single object:

| Concern | Question it answers | Why it changes independently |
|---|---|---|
| **Data source** | Where do the PDF bytes come from? | URL vs Buffer vs base64 vs filesystem path |
| **Parser session** | How is the PDF opened, decrypted, and managed? | Password, verbosity, open/destroy lifecycle |
| **Extraction operation** | What do you want out of the PDF? | Text, metadata, image, table, screenshot |

When these concerns are fused, adding a new extraction operation (e.g. `getAnnotations`) requires touching the same class as adding a new input type (e.g. `ReadableStream`), and isolating a Node-only method (e.g. `getHeader`) is impossible without a runtime check. The redesign places each concern in its own interface so each axis of change is isolated.

### 1.1 Why not a unified `extract(op, params)` interface?

The rubric proposes two patterns: separate extractor classes (`IExtractor<T>`) or a unified `extract(op, params)` dispatcher. The unified pattern is rejected for the following reasons:

- **Type safety is lost.** A single `extract('text', params)` call cannot express different return types per operation at compile time without complex discriminated unions.
- **Consumers pay for what they don't use.** A caller who only needs text must still import the full operation registry, which may include rendering dependencies.
- **Testing is harder.** A mock for `extract(op, params)` must handle every op string; a mock for `TextExtractor.extract()` handles exactly one contract.

The per-class pattern (`IExtractor<T>`) is chosen because it is type-safe, tree-shakeable, and independently testable.

---

## 2. Module Architecture

```
pdf-parse/
├── index.ts                 ← exports core (Node + browser)
│
├── core/
│   ├── IPDFSource.ts        ← loading layer interface
│   ├── IPDFParser.ts        ← parser/session layer interface
│   ├── PDFSession.ts        ← concrete IPDFParser implementation
│   ├── IExtractor.ts        ← generic extraction interface
│   ├── TextExtractor.ts
│   ├── MetadataExtractor.ts
│   ├── ImageExtractor.ts
│   ├── TableExtractor.ts
│   └── ScreenshotExtractor.ts
│
├── sources/
│   ├── UrlPDFSource.ts      ← Node + browser (fetch)
│   ├── BufferPDFSource.ts   ← Node + browser
│   └── Base64PDFSource.ts   ← Node + browser
│
├── renderers/
│   ├── IPageRenderer.ts     ← renderer interface (Node + browser)
│   ├── CanvasRenderer.ts    ← browser canvas API
│   └── PdfJsRenderer.ts     ← pdf.js (Node + browser)
│
└── node/
    ├── index.ts             ← exports node-only extensions
    ├── FilePDFSource.ts     ← fs/promises (Node only)
    ├── PuppeteerRenderer.ts ← headless Chrome (Node only)
    └── NodeExtractor.ts     ← getHeader() (Node only)
```

**Import path enforces platform constraints at build time:**
- `import { ... } from 'pdf-parse'` — safe in any environment
- `import { ... } from 'pdf-parse/node'` — Node.js only; bundlers exclude it from browser builds

---

## 3. Interface Definitions

### 3.1 `IPDFSource` — Data Source Layer

**Purpose:** Abstracts how raw PDF bytes are obtained. A source has no knowledge of parsing or extraction — it only knows how to produce bytes.

```typescript
/**
 * Represents any origin that can supply raw PDF bytes.
 *
 * Preconditions:
 *   - The underlying resource must exist and be accessible at call time.
 *   - For URL sources: the URL must be reachable and return a valid response.
 *   - For base64 sources: the string must be valid base64-encoded data.
 *
 * Postconditions:
 *   - load() resolves to a non-empty Uint8Array containing the full PDF bytes.
 *   - load() never resolves to an empty array.
 *   - load() never resolves to a partial result (all bytes or failure).
 *   - On failure, load() rejects with PdfSourceError — never silently.
 *
 * Invariants:
 *   - Calling load() multiple times on the same source returns equivalent
 *     byte sequences (idempotent for Buffer and Base64 sources; may differ
 *     for URL sources if the remote resource changes between calls).
 */
interface IPDFSource {
  /**
   * Fetch or read the raw PDF bytes.
   * @returns Promise resolving to the complete PDF as a Uint8Array.
   * @throws {PdfSourceError} network error, file not found, decode failure.
   */
  load(): Promise<Uint8Array>;
}
```

**Concrete implementations:**

```typescript
// ── Node + browser ────────────────────────────────────────────────────────

class UrlPDFSource implements IPDFSource {
  constructor(private readonly url: string) {}

  async load(): Promise<Uint8Array> {
    const res = await fetch(this.url);
    if (!res.ok) throw new PdfSourceError(`HTTP ${res.status}: ${this.url}`);
    return new Uint8Array(await res.arrayBuffer());
  }
}

class BufferPDFSource implements IPDFSource {
  constructor(private readonly data: Uint8Array) {}
  async load(): Promise<Uint8Array> { return this.data; }
}

class Base64PDFSource implements IPDFSource {
  constructor(private readonly b64: string) {}

  async load(): Promise<Uint8Array> {
    try {
      const binary = atob(this.b64);
      return Uint8Array.from(binary, c => c.charCodeAt(0));
    } catch {
      throw new PdfSourceError('Invalid base64 string');
    }
  }
}

// ── Node.js only — exported from 'pdf-parse/node' only ───────────────────

class FilePDFSource implements IPDFSource {
  constructor(private readonly path: string) {}

  async load(): Promise<Uint8Array> {
    const { readFile } = await import('node:fs/promises');
    return new Uint8Array(await readFile(this.path));
  }
}
```

**Rationale for this split:**
- A browser bundle includes only `UrlPDFSource`, `BufferPDFSource`, and `Base64PDFSource`. `FilePDFSource` is never bundled because it lives in `pdf-parse/node`.
- Adding a new source type (e.g. `S3PDFSource`, `ReadableStreamPDFSource`, `IndexedDBPDFSource`) requires implementing only `IPDFSource.load()` — zero changes to the session or extractor layers.
- Each source can be unit-tested in complete isolation by simply calling `source.load()` and asserting on the returned bytes.

---

### 3.2 `IPDFParser` — Parser / Session Layer

**Purpose:** Abstracts the lifecycle of an open PDF document. An `IPDFParser` implementation accepts an `IPDFSource`, opens the document, and exposes document-level properties (`pageCount`, `isEncrypted`). It is the single handoff point between the I/O world and the extraction world.

```typescript
/**
 * Manages the lifecycle of an open PDF document.
 *
 * Preconditions (for open()):
 *   - source must be a valid IPDFSource whose load() succeeds.
 *   - If the PDF is encrypted, opts.password must be the correct decryption key.
 *   - opts.verbosity must be 0, 1, or 2 if provided.
 *
 * Postconditions (after open()):
 *   - The returned parser has pageCount >= 1.
 *   - isEncrypted reflects the document's encryption state.
 *   - The parser is in the 'open' state; extraction operations may proceed.
 *
 * Postconditions (after destroy()):
 *   - All native resources are released.
 *   - Subsequent calls to any method on extractors derived from this parser
 *     throw PdfSessionClosedError.
 *   - Calling destroy() again is a no-op (idempotent).
 *
 * @throws {PdfLoadError}     if source bytes do not represent a valid PDF.
 * @throws {PdfPasswordError} if the PDF is encrypted and the password is
 *                            absent or incorrect.
 */
interface IPDFParser {
  readonly pageCount: number;
  readonly isEncrypted: boolean;

  /**
   * Open a PDF document from any IPDFSource.
   */
  open(
    source: IPDFSource,
    opts?: { password?: string; verbosity?: 0 | 1 | 2 }
  ): Promise<void>;

  /**
   * Release all native PDF resources.
   * Safe to call multiple times.
   */
  destroy(): void;
}
```

**Concrete implementation — `PDFSession`:**

```typescript
/**
 * PDFSession is the standard IPDFParser implementation.
 * Prefer the static factory over `new PDFSession()` to make
 * the success/failure contract explicit at the call site.
 */
class PDFSession implements IPDFParser {
  readonly pageCount: number = 0;
  readonly isEncrypted: boolean = false;

  /**
   * Factory method: creates and opens a session in one step.
   * Preferred over constructing and calling open() separately.
   *
   * @throws {PdfLoadError}     invalid or corrupt PDF bytes
   * @throws {PdfPasswordError} wrong or missing decryption password
   */
  static async open(
    source: IPDFSource,
    opts?: { password?: string; verbosity?: 0 | 1 | 2 }
  ): Promise<PDFSession> {
    const session = new PDFSession();
    await session.open(source, opts);
    return session;
  }

  async open(
    source: IPDFSource,
    opts?: { password?: string; verbosity?: 0 | 1 | 2 }
  ): Promise<void> {
    const bytes = await source.load();
    // ... initialise native PDF handle with bytes and opts
  }

  destroy(): void {
    // ... release native handle; mark session closed
  }
}
```

**Rationale for `IPDFParser` as a separate interface from `IPDFSource`:**
The source layer answers "where do the bytes come from?" The parser layer answers "how do I open and manage the live document?" These change for different reasons:
- The source changes when you add a new input type (S3, IndexedDB, ReadableStream).
- The parser changes when you change the underlying PDF engine (e.g. swap `pdf.js` for `pdfium-wasm`) or add session-level options (e.g. font substitution hints).

Keeping them separate means swapping the PDF engine requires only a new `IPDFParser` implementation — all sources and extractors remain unchanged.

---

### 3.3 `IExtractor<T>` — Extraction Layer

**Purpose:** A common contract for all extraction operations. Every concrete extractor accepts an `IPDFParser` (open session) in its constructor and exposes an `extract()` method that returns a typed result `T`.

```typescript
/**
 * Generic extraction interface.
 *
 * Type parameter T: the result type specific to this extraction operation.
 *   Examples: PageText[], PdfMetadata, ImageRef[], Table[], RenderedPage
 *
 * Preconditions:
 *   - The parser passed to the constructor must be open (not destroyed).
 *   - opts (if provided) must be valid for this operation:
 *       • page numbers must be integers in range 1..parser.pageCount
 *       • scale (for rendering) must be > 0 and <= 4.0
 *
 * Postconditions:
 *   - extract() resolves to a value of type T — never null or undefined.
 *   - extract() does not mutate the parser state.
 *   - If T is an array type, an empty array is returned when no results
 *     are found (never null).
 *
 * @throws {PdfSessionClosedError} if the parser has been destroyed.
 * @throws {PdfParseError}         if extraction fails due to document content.
 * @throws {InvalidOptionsError}   if opts violate the preconditions above.
 */
interface IExtractor<T> {
  extract(opts?: Record<string, unknown>): Promise<T>;
}
```

**Concrete extractors — all implement `IExtractor<T>`:**

```typescript
// ── Return types ──────────────────────────────────────────────────────────

interface PageText {
  page: number;
  text: string;
}

interface PdfMetadata {
  title?: string;
  author?: string;
  subject?: string;
  keywords?: string[];
  creator?: string;
  producer?: string;
  createdAt?: Date;
  modifiedAt?: Date;
  pageCount: number;   // always present
  isEncrypted: boolean;
  pdfVersion?: string;
}

interface ImageRef {
  id: string;
  page: number;
  width: number;
  height: number;
  mimeType: 'image/jpeg' | 'image/png' | 'image/webp';
  sizeBytes: number;
}

interface ImageData extends ImageRef {
  data: Uint8Array;   // decoded pixel bytes
}

interface TableCell {
  row: number;
  col: number;
  rowSpan: number;
  colSpan: number;
  text: string;
}

interface Table {
  page: number;
  tableIndex: number;
  rows: number;
  cols: number;
  cells: TableCell[];
}

interface RenderOptions {
  page: number;
  scale?: number;          // default 1.0, max 4.0
  format?: 'png' | 'jpeg'; // default 'png'
}

interface RenderedPage {
  page: number;
  width: number;
  height: number;
  mimeType: 'image/png' | 'image/jpeg';
  data: Uint8Array;
}

// ── TextExtractor ─────────────────────────────────────────────────────────

interface TextOptions {
  pages?: number[];          // 1-indexed; default = all pages
  normalizeSpaces?: boolean; // default true
}

class TextExtractor implements IExtractor<PageText[]> {
  constructor(private readonly parser: IPDFParser) {}

  /**
   * Preconditions:  parser open; pages (if given) in 1..pageCount
   * Postconditions: returns PageText[] in page order; empty array if
   *                 the PDF has no text layer (image-only PDF)
   */
  extract(opts?: TextOptions): Promise<PageText[]>;

  /**
   * Convenience: returns all pages joined with '\n\n'.
   * Postcondition: never returns null; returns '' for image-only PDFs.
   */
  extractFull(opts?: TextOptions): Promise<string>;
}

// ── MetadataExtractor ─────────────────────────────────────────────────────

class MetadataExtractor implements IExtractor<PdfMetadata> {
  constructor(private readonly parser: IPDFParser) {}

  /**
   * Preconditions:  parser open
   * Postconditions: pageCount is always present; all other fields are
   *                 optional and absent (not null) when not set in the PDF
   */
  extract(): Promise<PdfMetadata>;
}

// ── ImageExtractor ────────────────────────────────────────────────────────

class ImageExtractor implements IExtractor<ImageRef[]> {
  constructor(private readonly parser: IPDFParser) {}

  /**
   * List embedded image metadata — does NOT decode pixel data.
   * Preconditions:  parser open; pages (if given) in 1..pageCount
   * Postconditions: returns [] if no images found (never null)
   */
  extract(opts?: { pages?: number[] }): Promise<ImageRef[]>;

  /**
   * Decode pixel data for one image by id.
   * Preconditions:  id must be from a prior extract() call on same parser
   * Postconditions: returns ImageData with non-empty data field
   * @throws {ImageNotFoundError} if id does not exist in the document
   */
  fetchOne(id: string): Promise<ImageData>;
}

// ── TableExtractor ────────────────────────────────────────────────────────

class TableExtractor implements IExtractor<Table[]> {
  constructor(private readonly parser: IPDFParser) {}

  /**
   * Preconditions:  parser open; pages (if given) in 1..pageCount
   * Postconditions: returns [] if no tables found; rowSpan and colSpan
   *                 always present (default 1) for all cells
   */
  extract(opts?: { pages?: number[] }): Promise<Table[]>;
}

// ── ScreenshotExtractor ───────────────────────────────────────────────────

class ScreenshotExtractor implements IExtractor<RenderedPage> {
  /**
   * renderer is injected — allows swapping implementations per platform.
   * See Section 3.4 for IPageRenderer and available implementations.
   */
  constructor(
    private readonly parser: IPDFParser,
    private readonly renderer: IPageRenderer
  ) {}

  /**
   * Preconditions:  parser open; page in 1..pageCount; scale in 0.1..4.0
   * Postconditions: returns RenderedPage with non-empty data field
   * @throws {PlatformError} if the injected renderer cannot run in
   *                         the current runtime environment
   */
  extract(opts?: RenderOptions): Promise<RenderedPage>;
}
```

---

### 3.4 `IPageRenderer` — Swappable Renderer

**Purpose:** Decouples the page-to-pixels rendering engine from the `ScreenshotExtractor`. The renderer is injected as a dependency, making it trivially swappable without changing the extractor or the session.

```typescript
/**
 * Abstracts the rendering engine used to convert a PDF page to image bytes.
 *
 * Preconditions:
 *   - parser must be open.
 *   - pageNumber must be in range 1..parser.pageCount.
 *   - scale must be in range 0.1..4.0.
 *
 * Postconditions:
 *   - Returns a non-empty Uint8Array of encoded image bytes.
 *   - The bytes conform to the requested format (PNG or JPEG).
 *
 * @throws {PlatformError} if this renderer cannot operate in the
 *                         current JavaScript runtime.
 */
interface IPageRenderer {
  render(
    parser: IPDFParser,
    pageNumber: number,
    opts: { scale: number; format: 'png' | 'jpeg' }
  ): Promise<Uint8Array>;
}

// ── Implementations ───────────────────────────────────────────────────────

/** Browser canvas API. Works in any browser. */
class CanvasRenderer implements IPageRenderer { ... }

/** pdf.js rendering engine. Works in browser and Node.js. */
class PdfJsRenderer implements IPageRenderer { ... }

/** Headless Chromium via Puppeteer. Node.js only — in 'pdf-parse/node'. */
class PuppeteerRenderer implements IPageRenderer { ... }
```

**Swapping renderers without touching the extractor:**

```typescript
// Test environment — lightweight mock, no rendering dependency
const mockRenderer: IPageRenderer = {
  render: async () => new Uint8Array([137, 80, 78, 71]) // fake PNG header
};
const extractor = new ScreenshotExtractor(session, mockRenderer);

// Browser — native canvas
const extractor = new ScreenshotExtractor(session, new CanvasRenderer());

// Node.js server — pixel-perfect via Puppeteer
const extractor = new ScreenshotExtractor(session, new PuppeteerRenderer());

// Serverless (no native addons) — pure JS pdf.js renderer
const extractor = new ScreenshotExtractor(session, new PdfJsRenderer());
```

---

### 3.5 `INodeExtensions` — Node-Only Surface

**Purpose:** Exposes capabilities that only make sense on Node.js. Lives exclusively in `pdf-parse/node` — the import path itself prevents browser inclusion.

```typescript
// ONLY importable from 'pdf-parse/node'
// import { NodeExtractor } from 'pdf-parse/node'

interface BookmarkNode {
  title: string;
  page: number;
  children: BookmarkNode[];
}

/**
 * Node.js-only document operations.
 *
 * Preconditions:
 *   - Must be running in a Node.js runtime.
 *   - parser must be open.
 *
 * Postconditions (getHeader):
 *   - Returns the document outline tree.
 *   - Returns [] (not null) if the PDF has no bookmarks.
 *
 * @throws {PlatformError} if called outside a Node.js runtime.
 */
interface INodeExtensions {
  getHeader(): Promise<BookmarkNode[]>;
}

class NodeExtractor implements INodeExtensions {
  constructor(private readonly parser: IPDFParser) {}
  async getHeader(): Promise<BookmarkNode[]> { /* ... */ }
}
```

---

## 4. How the Design Meets Each Rubric Requirement

### 4.1 Supports Node.js and browser — `getHeader` only in Node module

The platform constraint is enforced at **import time**, not at runtime:

| Capability | `import from 'pdf-parse'` (any runtime) | `import from 'pdf-parse/node'` (Node.js only) |
|---|---|---|
| `UrlPDFSource` | ✅ | ✅ |
| `BufferPDFSource` | ✅ | ✅ |
| `Base64PDFSource` | ✅ | ✅ |
| `FilePDFSource` | ❌ not exported | ✅ |
| `TextExtractor` | ✅ | ✅ |
| `MetadataExtractor` | ✅ | ✅ |
| `ImageExtractor` | ✅ | ✅ |
| `TableExtractor` | ✅ | ✅ |
| `ScreenshotExtractor` + `CanvasRenderer` | ✅ | ✅ |
| `ScreenshotExtractor` + `PuppeteerRenderer` | ❌ not exported | ✅ |
| `NodeExtractor.getHeader()` | ❌ not exported | ✅ |

A browser bundler resolving `pdf-parse` never sees the contents of `pdf-parse/node`. No runtime check is needed and no `PlatformError` can be triggered by a correct build.

---

### 4.2 Allows swapping implementations — `IPageRenderer` injection

`ScreenshotExtractor` depends on `IPageRenderer`, not on any concrete renderer. The concrete renderer is injected at construction time. This satisfies the Dependency Inversion Principle: the extractor depends on an abstraction, not an implementation.

**Coupling comparison:**

```typescript
// BEFORE (current pdf-parse): renderer is hardcoded inside the class
class PDFParse {
  async getScreenshot() {
    const canvas = require('canvas'); // hardcoded dependency
    // ... cannot be swapped without modifying this class
  }
}

// AFTER (redesigned): renderer is injected
class ScreenshotExtractor {
  constructor(parser: IPDFParser, renderer: IPageRenderer) {}
  // ... renderer can be anything that satisfies IPageRenderer
}
```

The same injection pattern applies to `IPDFSource`: passing a different source to `PDFSession.open()` changes where the bytes come from without touching the session or extractor code.

---

### 4.3 Reduces coupling between loading, parsing, and extraction

**Before — monolithic `PDFParse`:**

```
PDFParse
  ├── knows how to fetch a URL          (loading concern)
  ├── knows how to decode base64        (loading concern)
  ├── owns the native PDF handle        (parsing concern)
  ├── extracts text                     (extraction concern)
  ├── extracts images                   (extraction concern)
  ├── renders page screenshots          (rendering concern)
  └── reads Node.js filesystem         (platform concern)

Change to any one concern requires modifying the same class.
```

**After — separated interfaces:**

```
IPDFSource         ← only knows how to produce bytes
    ↓ consumed by
IPDFParser         ← only knows how to open/close a PDF document
    ↓ passed to
IExtractor<T>      ← only knows how to extract one thing from an open document
    ↓ uses
IPageRenderer      ← only knows how to render pixels (injected into ScreenshotExtractor)

INodeExtensions    ← separate module, separate import path, Node.js only
```

**Coupling reduction table:**

| Change | Classes affected (before) | Classes affected (after) |
|---|---|---|
| Add new input type (e.g. S3) | `PDFParse` | New `S3PDFSource` only |
| Swap PDF engine | `PDFParse` | New `IPDFParser` implementation only |
| Add new extraction op | `PDFParse` | New `IExtractor<T>` implementation only |
| Swap renderer | `PDFParse` | New `IPageRenderer` implementation only |
| Add Node-only feature | `PDFParse` (breaks browser) | `pdf-parse/node` only |

---

## 5. Complete Usage Example

```typescript
import { PDFSession, TextExtractor, TableExtractor, ScreenshotExtractor } from 'pdf-parse';
import { UrlPDFSource, CanvasRenderer } from 'pdf-parse';

// ── Step 1: define the source (loading layer) ─────────────────────────────
const source = new UrlPDFSource('https://example.com/annual-report.pdf');

// ── Step 2: open a parser session (parsing layer) ─────────────────────────
// PDFSession.open() calls source.load() internally.
// Throws PdfLoadError or PdfPasswordError on failure.
const session = await PDFSession.open(source, { verbosity: 0 });

// ── Step 3: compose and run extractors (extraction layer) ─────────────────
// Multiple extractors share the same open session — no re-parsing.
const textResult   = await new TextExtractor(session).extract({ pages: [1, 2, 3] });
const tables       = await new TableExtractor(session).extract({ pages: [4, 5] });
const screenshot   = await new ScreenshotExtractor(session, new CanvasRenderer())
                           .extract({ page: 1, scale: 1.5, format: 'png' });

// ── Step 4: release native resources ─────────────────────────────────────
session.destroy();

// ── Node.js only ──────────────────────────────────────────────────────────
import { NodeExtractor, FilePDFSource } from 'pdf-parse/node';

const fileSource  = new FilePDFSource('/data/report.pdf');
const nodeSession = await PDFSession.open(fileSource);
const bookmarks   = await new NodeExtractor(nodeSession).getHeader();
nodeSession.destroy();
```

---

## 6. Interface Contract Summary

| Interface | Layer | Pre-conditions | Post-conditions | Error types |
|---|---|---|---|---|
| `IPDFSource.load()` | Source | Resource reachable; base64 valid | Non-empty `Uint8Array` of full PDF bytes | `PdfSourceError` |
| `IPDFParser.open()` | Session | Valid `IPDFSource`; correct password | `pageCount ≥ 1`; session open | `PdfLoadError`, `PdfPasswordError` |
| `IPDFParser.destroy()` | Session | Session exists | Session closed; idempotent | — |
| `IExtractor<T>.extract()` | Extraction | Session open; opts valid | Value of type `T`; never `null`; array types return `[]` not `null` | `PdfSessionClosedError`, `PdfParseError`, `InvalidOptionsError` |
| `ImageExtractor.fetchOne(id)` | Extraction | `id` from prior `extract()` call | `ImageData` with non-empty `data` | `ImageNotFoundError` |
| `IPageRenderer.render()` | Rendering | `pageNumber` in range; renderer available | Encoded image bytes (PNG/JPEG) | `PlatformError` |
| `INodeExtensions.getHeader()` | Node-only | Node.js runtime; session open | `BookmarkNode[]`; `[]` if no bookmarks | `PlatformError` |
