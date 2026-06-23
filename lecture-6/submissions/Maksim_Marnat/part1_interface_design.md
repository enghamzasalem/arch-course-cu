# Part 1.2: Redesigned Interface Proposal

## Goals

- Minimal stable core.
- Separate: byte source → parser session → extraction.
- Node-only APIs outside core.

## Modules

1. `IPDFSource` — obtain PDF bytes.
2. `IPDFParser` — open session.
3. `IPDFExtractor` — extraction operations.
4. `INodePDFUtils` — Node: `getHeader`, etc.

## Interfaces (TypeScript pseudocode)

```ts
export type PDFSourceInput =
  | { kind: "url"; url: string; headers?: Record<string, string> }
  | { kind: "bytes"; data: Uint8Array }
  | { kind: "base64"; value: string };

export interface IPDFSource {
  load(input: PDFSourceInput): Promise<Uint8Array>;
}

export interface ParseOptions {
  password?: string;
  verbosity?: 0 | 1 | 2;
}

export interface IPDFParser {
  open(sourceBytes: Uint8Array, options?: ParseOptions): Promise<IPDFSession>;
}

export interface IPDFSession {
  extractor(): IPDFExtractor;
  close(): Promise<void>;
}

export interface PageRange {
  from?: number;
  to?: number;
}

export interface IPDFExtractor {
  getText(range?: PageRange): Promise<{ text: string; pages: number }>;
  getInfo(): Promise<{ metadata: Record<string, string>; pageCount: number }>;
  getImages(range?: PageRange): Promise<{ images: Array<{ page: number; mime: string; data: string }> }>;
  getTables(range?: PageRange): Promise<{ tables: Array<{ page: number; rows: string[][] }> }>;
  getScreenshots(params?: { pages?: number[]; scale?: number }): Promise<{ images: string[] }>;
}

export interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<{ status: number; contentType?: string; isPdf: boolean }>;
}
```

## Contracts

### `IPDFSource.load`

- **Pre:** one valid `kind`; `url` absolute when `kind: "url"`.
- **Post:** non-empty `Uint8Array`.
- **Errors:** `InvalidInputError`, `SourceUnavailableError`.

### `IPDFParser.open`

- **Pre:** `sourceBytes.length > 0`; non-empty `password` if set.
- **Post:** open session; `extractor()` available.
- **Errors:** `ParseInitError`.

### `IPDFExtractor.getText`

- **Pre:** session open; valid page range.
- **Post:** text + page count for range.
- **Errors:** `ExtractionError`.

## Packages

- `pdf-parse` — core: `IPDFSource`, `IPDFParser`, `IPDFExtractor`.
- `pdf-parse/node` — `INodePDFUtils`, Node loaders.
- `pdf-parse/browser` — loaders + worker setup.
