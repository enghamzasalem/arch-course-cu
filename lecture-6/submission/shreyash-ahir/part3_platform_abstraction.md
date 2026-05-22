# Part 3.2 — Platform Abstraction: Node vs. Browser

## The Problem

`getHeader` uses HTTP range requests to read only the PDF header from a URL,
without downloading the full file.  This is a pure Node.js capability: it
depends on `http.request` and range request negotiation, which are not
available in the browser.

If `getHeader` lives on the core `IPDFSession` interface, browser users are
exposed to a method that will fail at runtime.  If it lives in the browser
bundle, bundlers may include Node.js `http` module code, causing build
failures or bundle size inflation.

---

## Chosen Approach: Submodule Export

The library ships two entry points:

```
pdf-parse           → core (Node + browser)
pdf-parse/node      → core + Node extras (Node only)
```

In `package.json`:
```json
{
  "exports": {
    ".": {
      "browser": "./dist/browser/index.js",
      "node":    "./dist/node/index.js",
      "default": "./dist/node/index.js"
    },
    "./node": {
      "node":    "./dist/node/extras.js"
    }
  }
}
```

The `"browser"` condition is used automatically by Webpack, Vite, and
Rollup when bundling for the browser — the browser build never includes
`./dist/node/extras.js`.

---

## Interface Definitions

### Core (both platforms)

```typescript
// pdf-parse/src/interfaces.ts
export interface IPDFSource  { load(): Promise<Uint8Array>; }
export interface IPDFSession {
  readonly pageCount: number;
  open(source: IPDFSource): Promise<void>;
  close(): Promise<void>;
}
export interface IPDFExtractor<T> {
  extract(session: IPDFSession, options?: ExtractOptions): Promise<T>;
}
```

No mention of `getHeader`.  A browser bundler importing `pdf-parse` sees
only these interfaces and the concrete core extractors.

### Node extras (Node only)

```typescript
// pdf-parse/src/node/extras.ts
export interface INodePDFUtils {
  /**
   * Fetch only the PDF header via HTTP range request.
   * Does NOT download the full file.
   *
   * Precondition: url is a valid http/https URL pointing to a PDF.
   * Postcondition: Returns the raw PDF header bytes (first 1024 bytes).
   * Error: Throws PDFHeaderError if the server does not support range requests.
   */
  getHeader(url: string, options?: { timeout?: number }): Promise<Uint8Array>;
}

export class NodePDFUtils implements INodePDFUtils {
  async getHeader(url: string, options = {}): Promise<Uint8Array> {
    // Uses Node.js http.request with Range: bytes=0-1023
  }
}
```

---

## How Each Caller Uses the Design

### Browser caller — never sees `getHeader`

```typescript
import { URLSource, PDFSession, TextExtractor } from 'pdf-parse';
// ↑ resolves to dist/browser/index.js — no Node code included

const session = new PDFSession();
await session.open(new URLSource('https://cdn.example.com/doc.pdf'));
const text = await new TextExtractor().extract(session);
await session.close();
```

TypeScript will error if a browser caller tries to import from `pdf-parse/node`
because `package.json` does not allow that export under the `browser` condition.

### Node.js caller — opts into `getHeader`

```typescript
import { BufferSource, PDFSession, TextExtractor } from 'pdf-parse';
import { NodePDFUtils } from 'pdf-parse/node';
// ↑ only works in Node; no browser bundler will include this

const utils = new NodePDFUtils();
const header = await utils.getHeader('https://example.com/large.pdf');
// If header indicates this is the right file, proceed with full download:
const session = new PDFSession();
await session.open(new URLSource('https://example.com/large.pdf'));
```

The Node caller must make an explicit opt-in import.  If a developer forgets,
they simply do not have access to `getHeader` — there is no runtime error or
missing method on a shared class.

---

## Why Not Platform Detection + Conditional Export?

An alternative is to detect `typeof window` at runtime and conditionally
enable `getHeader`.  This is worse:

- The Node-specific code is still in the browser bundle (just gated).
- The type system cannot enforce that browser code never calls `getHeader`.
- A test that runs in Node could silently test a code path that will fail
  in the browser.

Submodule separation keeps the concerns structurally isolated, not just
conditionally hidden.  The course principle: interfaces should explicitly
describe what is provided, not implicitly hide what is not.
