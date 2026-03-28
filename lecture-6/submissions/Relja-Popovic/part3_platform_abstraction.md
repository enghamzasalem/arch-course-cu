## Chosen Approach: Submodule + Capability Interface

The two options are combined. A `pdf-parse/node` submodule exposes an `INodePDFUtils` capability interface that carries `getHeader`. The core `pdf-parse` package exports neither.

This gives two enforcement layers:
1. **Structural** — Node code lives in a separate entry point that browser bundlers never resolve.
2. **Typed** — `getHeader` belongs to `INodePDFUtils`, which is not part of `IPDFParser` or any core interface, so it cannot be called accidentally through the shared API.

---

## Package Export Configuration

```json
// package.json
{
  "exports": {
    ".": {
      "browser": "./dist/browser/index.js",
      "node":    "./dist/node/index.js",
      "default": "./dist/node/index.js"
    },
    "./node": {
      "node":    "./dist/node/node-extras.js",
      "default": null
    },
    "./sources": {
      "browser": "./dist/browser/sources.js",
      "node":    "./dist/node/sources.js"
    },
    "./extractors": "./dist/shared/extractors.js"
  },
  "browser": {
    "./dist/node/node-extras.js": false
  }
}
```

The `"./node"` entry resolves to `null` under the `default` condition and is mapped to `false` in the `browser` field. Any bundler targeting the browser that encounters `import … from "pdf-parse/node"` will either produce a build error or resolve to an empty module — it will never silently include Node code.

---

## Core Interface (shared)

`pdf-parse` exports only what works in both environments:

```typescript
// pdf-parse  (browser + Node)
export { IPDFSource }    from "./interfaces/IPDFSource";
export { IPDFParser }    from "./interfaces/IPDFParser";
export { IExtractor }    from "./interfaces/IExtractor";
export { PDFSession }    from "./PDFSession";
// Sources safe in both environments:
export { UrlSource }     from "./sources/UrlSource";
export { BufferSource }  from "./sources/BufferSource";
export { Base64Source }  from "./sources/Base64Source";
```

`getHeader` is not present anywhere in this export. A browser consumer who imports `pdf-parse` has no path to it — not at the type level, not at runtime.

---

## Node-Specific Capability Interface

`pdf-parse/node` adds `INodePDFUtils` and its implementation on top of the core exports:

```typescript
// INodePDFUtils.ts
interface INodePDFUtils {
  // Fetches only the PDF header via HTTP Range request.
  // Precondition:  must run in Node.js; server must support Range requests.
  // Postcondition: resolves with header metadata without downloading the full file,
  //or rejects with RangeRequestError if the server returns 200
  //instead of 206 Partial Content.
  getHeader(url: string): Promise<PDFHeaderInfo>;
}

interface PDFHeaderInfo {
  pdfVersion: string;
  fileSize:   number;
  isLinearized: boolean;
}
```

```typescript
// pdf-parse/node  (Node.js only)
export * from "pdf-parse";                    // re-exports all core interfaces
export { FileSource }    from "./sources/FileSource";  // fs.readFile — Node only
export { INodePDFUtils } from "./INodePDFUtils";
export { NodeUtils }     from "./NodeUtils";   // implements INodePDFUtils
```

---

## How a Browser User Never Depends on Node Code

Three independent enforcement points prevent Node code from reaching a browser build:

1. **Bundler condition** — webpack, Vite, and esbuild all resolve the `browser` export condition. `"./node": false` means the submodule does not exist in a browser build. An `import from "pdf-parse/node"` is a build-time error, not a silent inclusion.

2. **TypeScript** — with `"moduleResolution": "bundler"` the compiler resolves the same `exports` conditions. `INodePDFUtils` and `NodeUtils` do not appear in the type graph for any file that only imports `pdf-parse`. Calling `getHeader` in a browser project will not compile.

3. **No re-export from core** — even if a consumer bypasses the above, `getHeader` is not reachable through `IPDFParser` or any other core type. There is no fallback path.

---

## How a Node User Opts In to `getHeader`

The opt-in is a single explicit import:

```typescript
import { NodeUtils } from "pdf-parse/node";

const utils = new NodeUtils();

// Precondition met: Node.js environment, HTTP/HTTPS URL, Range-capable server
const header = await utils.getHeader("https://cdn.example.com/archive.pdf");

console.log(header.pdfVersion);    // "1.7"
console.log(header.fileSize);      // 8421376
console.log(header.isLinearized);  // true
```

A Node user who only needs text extraction never imports `pdf-parse/node` at all:

```typescript
import { UrlSource, PDFSession } from "pdf-parse";
import { TextExtractor } from "pdf-parse/extractors";
// NodeUtils is not in scope — not needed, not loaded
```

The submodule approach means the dependency is visible in code review and in the import graph. There is no ambient availability of Node-only capabilities; every use of `getHeader` requires a deliberate import that any reviewer can see and question.