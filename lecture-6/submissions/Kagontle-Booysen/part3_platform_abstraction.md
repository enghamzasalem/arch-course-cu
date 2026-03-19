# Task 3.2 — Platform Abstraction (Node vs Browser)
## pdf-parse v2.4.5 · Redesigned Interface

---

## 1. Chosen Approach

The design combines **two of the three options** from the rubric:

1. **Submodule split** — `pdf-parse` (core) vs `pdf-parse/node` (Node extras)
2. **Optional capability interface** — `INodePDFUtils` with `getHeader` and other
   Node-only operations

Platform detection (`if (typeof window !== 'undefined')`) is explicitly
**rejected** — see Section 5 for the rationale.

The two chosen options complement each other: the submodule enforces the
boundary at build time (a browser bundler cannot resolve `pdf-parse/node`),
while `INodePDFUtils` makes the Node-only contract explicit and type-safe at
development time.

---

## 2. Core Interface — Works in Node and Browser

The core package (`pdf-parse`) exports only capabilities that work in every
supported runtime: Node.js, browser, Next.js, Vercel Edge Functions, AWS
Lambda, and Cloudflare Workers.

### What is exported from `pdf-parse` (core)

```typescript
// pdf-parse/index.ts  — safe in every environment

export { IPDFSource }           from './core/IPDFSource';
export { IPDFParser, PDFSession } from './core/PDFSession';
export { IExtractor }           from './core/IExtractor';

// Sources (no fs, no Node-only APIs)
export { UrlPDFSource }         from './sources/UrlPDFSource';
export { BufferPDFSource }      from './sources/BufferPDFSource';
export { Base64PDFSource }      from './sources/Base64PDFSource';

// Extractors (no canvas peer dependency, no Node-only APIs)
export { TextExtractor }        from './core/TextExtractor';
export { MetadataExtractor }    from './core/MetadataExtractor';
export { ImageExtractor }       from './core/ImageExtractor';
export { TableExtractor }       from './core/TableExtractor';
export { ScreenshotExtractor }  from './core/ScreenshotExtractor';

// Renderers available without native addons
export { IPageRenderer }        from './renderers/IPageRenderer';
export { CanvasRenderer }       from './renderers/CanvasRenderer';
export { PdfJsRenderer }        from './renderers/PdfJsRenderer';

// Error types
export { PdfSourceError, PdfLoadError, PdfPasswordError,
         PdfParseError, PdfSessionClosedError,
         ImageNotFoundError, PlatformError } from './core/errors';
```

### What the core package never contains

| Excluded from core | Reason |
|---|---|
| `require('fs')` or `import('node:fs/promises')` | Crashes in browsers and Workers |
| `require('canvas')` or `import('canvas')` | Native addon, not available in browsers |
| `require('puppeteer')` | Headless Chrome, Node-only |
| `getHeader()` | Depends on Node PDF engine outline API |
| `FilePDFSource` | Uses `fs.readFile` |
| `PuppeteerRenderer` | Requires Puppeteer |
| Runtime platform checks (`process`, `window`) | Leaks platform knowledge into core |

---

## 3. `INodePDFUtils` — Optional Capability Interface

The Node-only surface is expressed as a typed capability interface. This makes
the contract explicit and discoverable at development time — a developer using
TypeScript sees exactly what operations are available on Node, with full
autocomplete and type checking.

```typescript
// pdf-parse/node/INodePDFUtils.ts

interface BookmarkNode {
  title:    string;
  page:     number;
  level:    number;
  children: BookmarkNode[];
}

/**
 * Optional capability interface for Node.js-only PDF operations.
 *
 * This interface is only available via 'pdf-parse/node'.
 * It is never part of the core IPDFParser or IExtractor interfaces.
 *
 * Preconditions:
 *   - parser must be an open PDFSession (not destroyed).
 *   - Must be called in a Node.js runtime (not browser, not Workers).
 *
 * @throws {PlatformError} if called outside a Node.js runtime.
 */
interface INodePDFUtils {
  /**
   * Extract the document outline (bookmarks / table of contents).
   *
   * Preconditions:  parser open; Node.js runtime
   * Postconditions: returns BookmarkNode[] tree; [] if PDF has no outline
   * @throws {PlatformError}         if called outside Node.js
   * @throws {PdfSessionClosedError} if parser has been destroyed
   */
  getHeader(parser: IPDFParser): Promise<BookmarkNode[]>;
}
```

### Concrete implementation — `NodePDFUtils`

```typescript
// pdf-parse/node/NodePDFUtils.ts

import { IPDFParser, PlatformError } from 'pdf-parse';

class NodePDFUtils implements INodePDFUtils {
  /**
   * Runtime guard: if somehow called outside Node.js, throw immediately
   * rather than producing an opaque native error.
   */
  private assertNodeRuntime(): void {
    if (typeof process === 'undefined' || process.versions?.node === undefined) {
      throw new PlatformError(
        'NodePDFUtils.getHeader() requires Node.js. ' +
        'Import from "pdf-parse/node" only in Node.js environments.'
      );
    }
  }

  async getHeader(parser: IPDFParser): Promise<BookmarkNode[]> {
    this.assertNodeRuntime();
    // Access the document outline via the underlying pdf-parse engine
    const outline = await parser._nativeHandle.getOutline();
    return outline ? mapOutline(outline) : [];
  }
}

function mapOutline(nodes: unknown[], level = 0): BookmarkNode[] {
  return (nodes as any[]).map(n => ({
    title:    n.title ?? '',
    page:     n.dest?.[0] ?? 0,
    level,
    children: n.items?.length ? mapOutline(n.items, level + 1) : [],
  }));
}
```

---

## 4. `pdf-parse/node` Submodule — Full Export List

```typescript
// pdf-parse/node/index.ts  — Node.js only

// Re-export everything from core so Node users have one import path
export * from 'pdf-parse';

// Node-only sources
export { FilePDFSource }    from './FilePDFSource';

// Node-only renderers
export { PuppeteerRenderer } from './PuppeteerRenderer';

// Node-only capability interface and implementation
export { INodePDFUtils }    from './INodePDFUtils';
export { NodePDFUtils }     from './NodePDFUtils';

// Convenience: pre-wired NodePDFUtils singleton
export const nodePDF = new NodePDFUtils();
```

The `package.json` `exports` field enforces that `pdf-parse/node` is only
resolvable in Node.js environments:

```json
{
  "name": "pdf-parse",
  "exports": {
    ".": {
      "import":  "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "browser": "./dist/browser.mjs"
    },
    "./node": {
      "node":    "./dist/node/index.mjs",
      "default": null
    }
  }
}
```

The `"browser": "./dist/browser.mjs"` entry ensures browser bundlers (webpack,
Rollup, Vite) receive a bundle that has no Node-only code even if a dependency
accidentally imports from the root. The `"./node"` subpath has `"default": null`
— any non-Node resolution attempt returns `null`, producing a build-time error
rather than a silent runtime failure.

---

## 5. How a Browser User Never Depends on Node Code

### Layer 1 — Package `exports` field (build time)

The `exports` map in `package.json` is the first line of defence. When a browser
bundler resolves `pdf-parse/node`, it hits `"default": null` and emits a build
error immediately. The browser bundle never contains `fs`, `canvas`, or
`puppeteer` code.

### Layer 2 — TypeScript module resolution (development time)

`pdf-parse/node` has its own `types` field pointing to Node-only type
declarations. A browser TypeScript project that tries to import
`INodePDFUtils` receives a type error at compile time — before the code runs.

### Layer 3 — Tree-shaking (bundle time)

Because `FilePDFSource`, `PuppeteerRenderer`, and `NodePDFUtils` are only
exported from `pdf-parse/node` (never from `pdf-parse`), a browser bundle
that imports only from `pdf-parse` will never include these modules even if
the bundler does not perform dead-code elimination.

### Layer 4 — Runtime guard (safety net)

`NodePDFUtils.assertNodeRuntime()` checks `process.versions?.node` before
every Node-only call. If all three layers above are somehow bypassed, the
runtime guard throws a descriptive `PlatformError` rather than an opaque
native crash.

```
Browser developer experience:

import { getHeader } from 'pdf-parse';
  → TypeScript: Module '"pdf-parse"' has no exported member 'getHeader'. ✗

import { NodePDFUtils } from 'pdf-parse/node';
  → Bundler: Cannot resolve 'pdf-parse/node' in browser target. ✗

// Both errors happen before the code ships to users.
```

---

## 6. How a Node User Opts In to `getHeader`

A Node.js developer explicitly opts in by importing from the `/node` subpath.
The import itself communicates the intent — there is no ambiguity about which
environment the code targets.

```typescript
// Node.js server — opt-in to getHeader
import { PDFSession, TextExtractor } from 'pdf-parse';
import { FilePDFSource, nodePDF }    from 'pdf-parse/node';

async function extractWithOutline(filePath: string) {
  const source  = new FilePDFSource(filePath);
  const session = await PDFSession.open(source);

  // Core interface — works everywhere
  const text = await new TextExtractor(session).extractFull();

  // Node-only opt-in — only because we imported from 'pdf-parse/node'
  const outline = await nodePDF.getHeader(session);

  session.destroy();
  return { text, outline };
}
```

The opt-in is **explicit and minimal**: one additional import line. The core
extraction code is unchanged; `getHeader` is composed alongside it rather than
replacing it.

### Opt-in comparison table

| Scenario | Import path | `getHeader` available? | Core extractors available? |
|---|---|---|---|
| Browser app | `pdf-parse` only | ❌ (build error if attempted) | ✅ |
| Node.js, core only | `pdf-parse` only | ❌ (type error if attempted) | ✅ |
| Node.js, full | `pdf-parse` + `pdf-parse/node` | ✅ | ✅ |
| Cloudflare Worker | `pdf-parse` only | ❌ (build error if attempted) | ✅ |
| Next.js (browser bundle) | `pdf-parse` only | ❌ | ✅ |
| Next.js (server bundle) | `pdf-parse` + `pdf-parse/node` | ✅ | ✅ |

---

## 7. Why Platform Detection Was Rejected

The rubric lists "platform detection and conditional export" as an option.
This approach was considered and rejected for the following reasons:

```typescript
// REJECTED PATTERN — platform detection in core

class PDFParse {
  async getHeader() {
    if (typeof window !== 'undefined') {
      // Browser
      throw new PlatformError('getHeader is not available in browser');
    }
    // Node.js
    return this._getOutline();
  }
}
```

**Problems with this approach:**

| Problem | Impact |
|---|---|
| `getHeader` appears on the core class | Browser consumers see the method and must handle a runtime error |
| The method ships in every bundle | Increases browser bundle size even though it is unusable |
| Failure is at runtime, not build time | A browser user discovers the error in production, not during development |
| `typeof window` is not a reliable Node.js check | Service workers, jsdom test environments, and some edge runtimes have `window` but are not browsers |
| Violates Least Astonishment | A method that is present but always throws is a broken contract |

The submodule + capability interface approach catches the platform mismatch at
build time (bundler error) and development time (TypeScript error), which is
strictly better than a runtime exception.

---

## 8. Summary

| Concern | Where it lives | Enforcement mechanism |
|---|---|---|
| Core extractors (`getText`, `getInfo`, `getImage`, `getTable`, `getScreenshot`) | `pdf-parse` | Always available; no restriction |
| Browser-safe renderer (`CanvasRenderer`) | `pdf-parse` | Included in browser bundle |
| Node-compatible renderer (`PdfJsRenderer`) | `pdf-parse` | Works in both environments |
| Node-only renderer (`PuppeteerRenderer`) | `pdf-parse/node` | `exports` field → build error in browser |
| Node-only source (`FilePDFSource`) | `pdf-parse/node` | `exports` field → build error in browser |
| Node-only operations (`getHeader`) | `pdf-parse/node` via `INodePDFUtils` | Type error + build error + runtime guard |
