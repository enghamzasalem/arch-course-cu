# Part 3.2: Platform Abstraction (Node vs Browser)

This document describes how **Node-specific features** (e.g. `getHeader`) are kept **out of the core interface** so that the core remains reusable in Node and browser, and how Node users can still opt in to those features.

---

## 1. Separation of Core vs Node-Only

| Layer        | Contents                                                                 | Platform   |
|-------------|---------------------------------------------------------------------------|------------|
| **Core**    | getText, getInfo, getImage, getTable, getScreenshot, destroy               | Node + browser |
| **Node-only** | getHeader(url, validate?) — HTTP range request, magic bytes, no full download | Node only  |

The core interface is the same in all environments. Node-specific behavior is available only when the Node module is used and the consumer explicitly uses the extra API.

---

## 2. Chosen Approach: Optional Capability Interface + Submodule

We combine two mechanisms:

### 2.1 Core package: `pdf-parse` (or `pdf-parse/core`)

- Exports: **IPDFSource**, **IPDFParser** / **IPDFSession**, **IPDFExtractor** (or the current `PDFParse` class with only cross-platform methods).
- Methods: `getText()`, `getInfo()`, `getImage()`, `getTable()`, `getScreenshot()`, `destroy()`.
- No `getHeader`. No Node-only APIs. Works in Node and browser via different implementations (e.g. different worker or loader).

### 2.2 Node extras: `pdf-parse/node` or capability interface `INodePDFUtils`

- **Option A — Submodule:**  
  `import { PDFParse } from 'pdf-parse'` gives the core.  
  `import { getHeader } from 'pdf-parse/node'` gives Node-only helpers.  
  `getHeader(url, validate?)` is a standalone function or a mixin that Node users import when they need it.

- **Option B — Capability interface:**  
  Core exports a type/interface that Node build implements:

  ```ts
  // Core (shared)
  interface IPDFExtractor {
    getText(params?): Promise<string>;
    getInfo(): Promise<Metadata>;
    getImage(params?): Promise<Image[]>;
    getTable(params?): Promise<Table[]>;
    getScreenshot(params?): Promise<PageImage[]>;
    destroy(): void;
  }

  // Node-only extension
  interface INodePDFUtils {
    getHeader(url: string, validate?: boolean): Promise<HeaderResult>;
  }

  // In Node: PDFParse implements IPDFExtractor & INodePDFUtils
  // In browser: PDFParse implements only IPDFExtractor
  ```

  Node users who need `getHeader` use the Node build and call `parser.getHeader(url)`. Browser build does not implement `INodePDFUtils`, so `getHeader` is never present there.

- **Option C — Platform detection and conditional export:**  
  Main entry `pdf-parse` resolves to `pdf-parse/node` or `pdf-parse/browser` based on `package.json` `"browser"` field or environment. The **node** export includes `getHeader`; the **browser** export does not. So the same import path gives a different surface per environment.

**Recommended:** Option A (submodule) or B (capability interface). Both keep the core contract clean and make Node-only behavior explicit and opt-in.

---

## 3. How a Browser User Never Depends on Node Code

1. **Separate build:** The library ships a **browser** build (e.g. `dist/browser.js` or `pdf-parse/browser`). That build:
   - Does not include `getHeader` or any Node-only APIs (no `http`, `https`, `fs`).
   - Implements only the core interface (getText, getInfo, getImage, getTable, getScreenshot, destroy).
   - Uses only browser-safe APIs (e.g. Web Workers, ArrayBuffer, fetch if needed).

2. **Bundler resolution:** With `"browser": { "pdf-parse/node": false }` or conditional exports, a browser bundler never pulls in `pdf-parse/node`. So browser code cannot even reference `getHeader` without a build error or missing export.

3. **No Node-only in core types:** The public TypeScript types for the core module do not mention `getHeader`. Only the Node-specific types (e.g. `INodePDFUtils` or `pdf-parse/node`) document it. So browser-only users never see it in the core API.

Result: **Browser users depend only on the core; they never load or depend on Node-only code.**

---

## 4. How a Node User Can Opt In to getHeader

1. **Explicit import:**  
   `const { getHeader } = require('pdf-parse/node');`  
   Use when you only need header inspection (e.g. check PDF magic bytes without downloading the full file).

2. **Extended parser (if using capability interface):**  
   `const parser = new PDFParse({ url });`  
   In Node, `parser` may implement `INodePDFUtils`, so `parser.getHeader(url, true)` is available. TypeScript/IDE shows `getHeader` only when using the Node typings.

3. **Documentation:**  
   README or “Node only” section states: “`getHeader` is available only in Node. Use `require('pdf-parse/node')` or the Node build of `PDFParse`.” So Node users who need it know where to find it; others ignore it.

---

## 5. Summary

| Concern              | Approach                                                                 |
|----------------------|--------------------------------------------------------------------------|
| Core interface       | Same in Node and browser: getText, getInfo, getImage, getTable, getScreenshot, destroy. |
| Node-only (getHeader)| Separate submodule (`pdf-parse/node`) or capability interface (`INodePDFUtils`). |
| Browser              | Uses only core build; never imports Node-only code; no `getHeader` in types or bundle. |
| Node opt-in          | Import `pdf-parse/node` or use Node build of parser that implements `getHeader`. |

This keeps the core API reusable and stable across platforms while allowing Node users to opt in to platform-specific features without affecting browser or other consumers.

---
## 6. Design Benefit

This separation ensures that:

- The core API remains stable and portable across environments.
- Platform-specific features do not leak into the global interface.
- The system is easier to maintain and extend in the future.

For example, additional platform-specific features (e.g. Node streaming or browser canvas rendering) can be added without modifying the core API.