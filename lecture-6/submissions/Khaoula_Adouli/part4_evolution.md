# Part 4.1: v1 → v2 Migration and Future Evolution

This document proposes how to **deprecate pdf-parse v1 cleanly**, what **v2 improves for reusability**, and **one backward-compatible evolution** for a future v2.5 or v3.

---

## 1. v1 vs v2: What Changed

**v1 (function-based):**
```js
const pdf = require('pdf-parse');
pdf(buffer).then(r => r.text);  // single function, returns { text, info, ... }
```

**v2 (class-based):**
```js
const { PDFParse } = require('pdf-parse');
const parser = new PDFParse({ data: buffer });
const text = await parser.getText();
parser.destroy();
```

v2 introduces an **instance lifecycle**, explicit **configuration** (url vs data vs base64), **per-method extraction** (getText, getInfo, …), and **destroy()** for resource cleanup. This improves reusability: one instance per PDF, clear lifecycle, and the same interface across environments.

---

## 2. Deprecating v1 Cleanly

### 2.1 Warnings

- In v2.x, keep the old **function export** but wrap it so it:
  - Logs a **deprecation warning** once per process:  
    `"pdf-parse(buffer) is deprecated; use new PDFParse({ data: buffer }).getText() instead. See migration guide: ..."`
  - Internally creates a temporary `PDFParse` instance, calls `getText()` (and optionally `getInfo()`), then `destroy()`, and returns a v1-shaped object `{ text, info, ... }` so existing v1 code keeps working.

- Use a **single warning** (e.g. `process.emitWarning` or `console.warn` guarded by a global flag) to avoid log spam.

### 2.2 Migration Guide

Provide a short **migration guide** in the README or docs:

| v1 usage | v2 equivalent |
|----------|----------------|
| `pdf(buffer).then(r => r.text)` | `const p = new PDFParse({ data: buffer }); const text = await p.getText(); p.destroy();` |
| `pdf(buffer).then(r => r.info)` | `const p = new PDFParse({ data: buffer }); const info = await p.getInfo(); p.destroy();` |
| No cleanup | Always call `parser.destroy()` when done (or use try/finally) |

- Document that v1 will be **removed in v3** (or next major), and recommend moving to v2 for better control and reusability (lifecycle, multiple operations per instance, cross-platform clarity).

### 2.3 Timeline

- **v2.0–2.x:** v1 API deprecated but still supported; warning on use.
- **v3.0:** Remove the legacy function export; only the class-based API is supported.

---

## 3. What v2 Improves for Reusability

- **Instance lifecycle:** One parser instance per PDF; explicit `destroy()` so long-running servers and batch jobs can avoid leaks. Reusable in loops and request handlers.
- **Configurable source:** Same class accepts URL, Buffer, or base64; one interface for all environments (Node, browser, CLI).
- **Per-method extraction:** getText, getInfo, getImage, getTable, getScreenshot allow consumers to call only what they need and reuse the same instance for multiple operations.
- **Configurable worker / backend:** v2 allows different worker paths or renderers, so the same interface can be reused with different implementations (e.g. for screenshots).
- **Clear platform boundary:** Node-only features (e.g. getHeader) can be separated (submodule or capability interface), so the core stays reusable across Node and browser.

---

## 4. One Backward-Compatible Evolution: v2.5 or v3

**Proposal:** Add an optional **streaming** option to **getText** for large files, and add **getLinks** with an optional parameter. Both are backward-compatible.

### 4.1 Optional stream option for getText

**Change:**  
`getText(params?: { pages?: [number, number]; stream?: boolean })`

- **stream: false (default):** Behavior unchanged; returns a single `Promise<string>` with full text.
- **stream: true:** Returns an **async iterable** or **ReadableStream** of text chunks (e.g. per page or per region), so callers can process large PDFs without loading the entire string in memory.

**Compatibility:** Existing `getText()` and `getText({ pages: [1, 3] })` remain valid; new code can opt in to `getText({ stream: true })`. No breaking change.

**Migration note:** “For very large documents, use getText({ stream: true }) to get an async iterator of chunks. Default behavior is unchanged.”

### 4.2 Optional getLinks with followExternal

**Change:** New method (or new op in a unified `extract` interface):

- `getLinks(params?: { followExternal?: boolean }): Promise<Link[]>`  
  Returns links found in the PDF. **followExternal: false (default):** only in-document links or raw URIs. **followExternal: true:** optionally resolve external URLs (e.g. for link validation); implementation may limit or throttle.

**Compatibility:** New method; no existing API is removed or changed. Old code is unaffected.

**Migration note:** “v2.5 adds getLinks(). Use getLinks({ followExternal: true }) only when you need to validate external URLs; default is false for performance.”

### 4.3 Summary of evolution

| Change | Backward compatible? | Migration |
|--------|------------------------|-----------|
| getText({ stream: true }) | Yes (optional param) | Use for large files; default unchanged. |
| getLinks({ followExternal?: boolean }) | Yes (new method) | Adopt when needed; no change for existing callers. |

---

## 5. Summary

- **v1 deprecation:** Warn on use of the legacy function; provide a small migration guide; remove in v3.
- **v2 reusability:** Instance lifecycle, destroy(), multiple sources, per-method extraction, and a clear core/platform split improve reuse across Node, browser, and CLI.
- **Future (v2.5/v3):** Add optional streaming for getText and getLinks with optional followExternal; both additions are backward-compatible and documented with short migration notes.
