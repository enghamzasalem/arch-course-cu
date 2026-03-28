## Interface Definitions

### `IPDFSource` – Data Source Abstraction

```typescript
interface IPDFSource {
  // Returns the raw PDF bytes, fetching or decoding as needed.
  // Precondition:  the underlying resource must exist and be accessible.
  // Postcondition: resolves to a Uint8Array of valid PDF bytes,
  //or rejects with PDFSourceError describing the failure.
  load(): Promise<Uint8Array>;

  // Releases any held resources (network connections, file handles).
  // Postcondition: safe to call multiple times; never throws.
  dispose(): void;
}
```

**Concrete implementations:**
```typescript
class UrlSource    implements IPDFSource { constructor(url: string) }
class BufferSource implements IPDFSource { constructor(data: Uint8Array) }
class Base64Source implements IPDFSource { constructor(data: string) }
// Node-only:
class FileSource   implements IPDFSource { constructor(path: string) }
```

**Rationale:** Isolating the source means the parser and extractors never need to know whether the bytes came from a network request, a file, or an in-memory buffer. Implementations can be swapped freely — e.g. replacing `UrlSource` with a caching proxy — without touching any other
layer.

---

### `IPDFParser` – Parser Session Lifecycle

```typescript
interface IPDFParser {
  // Number of pages in the open document. Valid only after open() resolves.
  readonly pageCount: number;

  // Opens a PDF from the given source.
  // Precondition:  source.load() must succeed; open() must not already have been called.
  // Postcondition: pageCount is set; the session is ready for extraction.
  //                Rejects with PDFPasswordError if encrypted and no password supplied,
  //                or PDFParseError if the bytes are not a valid PDF.
  open(source: IPDFSource, options?: { password?: string; workerSrc?: string }): Promise<void>;

  // Releases the underlying worker and all document memory.
  // Precondition:  open() must have resolved successfully.
  // Postcondition: any subsequent extraction call throws SessionClosedError.
  //                Safe to call multiple times.
  close(): Promise<void>;
}
```

**Rationale:** Making the session lifecycle explicit (open / close) means the same parsed document can be queried multiple times — e.g. `getText` and `getInfo` in parallel — without re-parsing the PDF. It also makes the worker's lifetime auditable and testable.

---

### `IExtractor<T>` – Generic Extraction Pattern

```typescript
interface IExtractor<T> {
  // Runs the extraction against an open parser session.
  // Precondition:  parser.open() must have resolved; parser must not be closed.
  //pages, if provided, must be a subset of [1 … parser.pageCount].
  // Postcondition: resolves with a value of type T,
  //or rejects with ExtractionError on failure.
  //Never mutates the parser session's internal state.
  extract(parser: IPDFParser, params?: { pages?: number[] }): Promise<T>;
}
```

**Concrete extractors:**
```typescript
class TextExtractor       implements IExtractor<TextResult>       { }
class InfoExtractor       implements IExtractor<InfoResult>       { }
class ImageExtractor      implements IExtractor<EmbeddedImage[]>  { }
class TableExtractor      implements IExtractor<TableResult[]>    { }
class ScreenshotExtractor implements IExtractor<ScreenshotResult[]> { }
```

Each extractor can accept additional typed params via a subtype of the base params:
```typescript
class ScreenshotExtractor implements IExtractor<ScreenshotResult[]> {
  extract(parser, params?: { pages?: number[]; scale?: number; format?: 'png' | 'jpeg' }): Promise<ScreenshotResult[]>;
}
```

**Rationale:** A single shared interface makes all extractors interchangeable. Calling code, caching layers, retry wrappers, and tests can operate on `IExtractor<T>` without knowing which operation is being performed. Swapping the screenshot renderer is as simple as passing a different `ScreenshotExtractor` implementation.

---

## How the Design Addresses Each Requirement

### Node.js vs Browser

`getHeader` — the current Node-only method — is removed from the shared interface entirely. It lives only in a Node-specific module (`pdf-parse/node`) and is never present in the browser build:

```typescript
// pdf-parse/node only — not exported from the core package
class NodeUtils {
  // Precondition:  must run in Node.js; server must support HTTP Range requests.
  // Postcondition: resolves with header metadata without downloading the full file,
  //                or rejects with RangeRequestError if the server returns 200 instead of 206.
  getHeader(url: string): Promise<PDFHeaderInfo>;
}
```

Browser consumers import `pdf-parse` and never see `NodeUtils`. The package `exports` field maps the `browser` condition to a build that excludes it entirely, making the restriction a build-time error rather than a runtime surprise.

### Swapping Implementations

Because every extractor implements `IExtractor<T>`, any implementation can be substituted without changing the calling code:

```typescript
// Production: real renderer
const extractor: IExtractor<ScreenshotResult[]> = new ScreenshotExtractor();

// Test: deterministic mock
const extractor: IExtractor<ScreenshotResult[]> = new MockScreenshotExtractor();

// Either way, the call site is identical:
const pages = await extractor.extract(parser, { pages: [1], scale: 2 });
```

The same pattern applies to `IPDFSource`: swapping `UrlSource` for a `CachedUrlSource` that checks a local disk cache requires no changes to the parser or extractors.

### Reduced Coupling

Each layer depends only on the interface above it, never on a concrete class:

```
IPDFSource  ──(load)──►  IPDFParser  ──(open)──►  IExtractor<T>
    ▲                         ▲                         ▲
UrlSource               PDFSession               TextExtractor
BufferSource                                     TableExtractor
Base64Source                                     …
```

`PDFSession` only calls `source.load()` — it does not know whether the source is a URL or a file. `TextExtractor` only calls methods on `IPDFParser` — it does not know how the document was loaded or which worker is running. This means each layer can be developed, tested, and replaced
independently.