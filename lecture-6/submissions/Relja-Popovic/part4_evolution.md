## v1 → v2 Transition

### The Breaking Change

```js
// v1 — single function, result available once, worker created and destroyed internally
pdf(buffer).then(r => console.log(r.text));

// v2 — class instance, explicit lifecycle, multiple operations on one parse
const parser = new PDFParse({ data: buffer });
const result = await parser.getText();
await parser.destroy();
```

### Deprecating v1 Cleanly

**Phase 1 – Soft deprecation (one minor release)**

Ship a compatibility shim that keeps `pdf()` working but emits a warning on first call per process. The `once` flag prevents flooding production logs.

```js
/** @deprecated Use `new PDFParse({ data })` instead. Will be removed in v3. */
function pdf(buffer, options) {
  process.emitWarning(
    "pdf() is deprecated. Migrate to: new PDFParse({ data: buffer }).getText()\n" +
    "Guide: https://docs.pdf-parse.dev/migration/v1-to-v2",
    { code: "PDF_PARSE_DEPRECATED", once: true }
  );
  const parser = new PDFParse({ data: buffer, ...options });
  return parser.getText().finally(() => parser.destroy());
}
```

**Phase 2 – Hard deprecation (next minor release)**

Remove `once: true`. The warning fires on every call so CI pipelines that were suppressing it previously will now surface it consistently.

**Phase 3 – Removal (next major, v3)**

Delete the shim. Replace with a clear throw:

```js
function pdf() {
  throw new Error(
    "pdf() was removed in pdf-parse v3. " +
    "Migrate to: new PDFParse({ data: buffer }).getText()"
  );
}
```

**Migration guide (published alongside Phase 1)**

```
Before:  pdf(buffer).then(r => r.text)
After:   const p = new PDFParse({ data: buffer });
         const { text } = await p.getText();
         await p.destroy();

Why: v2 lets you call getText() and getInfo() on the same parse without reloading the PDF.
     destroy() gives you explicit control over when the worker thread is released.
```

### What v2 Improves for Reusability

| Concern | v1 | v2 |
|---|---|---|
| Worker lifetime | Created and destroyed per call — no control | Explicit `destroy()` — caller decides when to release |
| Multiple operations | Required re-parsing the PDF for each operation | One `open`, many extractions on the same session |
| Worker configuration | Hardcoded internal path | `workerSrc` accepted in constructor — swappable per environment |
| Encrypted PDFs | Password had to be passed on every call | Passed once at construction, reused for all operations |
| Testability | Entire function had to be mocked | Class can be mocked at the interface boundary |

---

## Proposed v2.5 Evolution: `getLinks()`

### What changes

A new `LinkExtractor` class is added to `pdf-parse/extractors`. It implements the existing `IExtractor<T>` interface, so it slots into the architecture with no changes to any existing type or class.

```typescript
interface LinkResult {
  pageNumber:  number;
  type:        "internal" | "external";
  // internal: 1-based destination page number as a string e.g. "4"
  // external: full URL string e.g. "https://example.com"
  destination: string;
  // bounding box in PDF user units [x, y, width, height]
  rect: [number, number, number, number];
}

interface LinkExtractionParams extends ExtractionParams {
  // If true, each external URL is HEAD-requested to check whether it resolves.
  // Only meaningful in Node.js; silently ignored in browser/edge environments.
  // Default: false
  followExternal?: boolean;
}

class LinkExtractor implements IExtractor<LinkResult[]> {
  extract(
    parser: IPDFParser,
    params?: LinkExtractionParams
  ): Promise<LinkResult[]>;
}
```

### Usage

```typescript
import { LinkExtractor } from "pdf-parse/extractors";

// Basic — works in all environments
const links = await new LinkExtractor().extract(session);

// With reachability check — Node.js only, opt-in
const links = await new LinkExtractor().extract(session, { followExternal: true });
links.forEach(l => console.log(l.destination, l.type));
```

### What stays compatible

- No existing class, interface, or method is modified.
- `LinkExtractor` is an additive export — consumers who do not import it are unaffected.
- `followExternal: false` (the default) produces identical behaviour in all environments,
  so the same calling code runs in Node and browser without branching.
- Semver: this is a **minor bump** (v2.4.x → v2.5.0). No migration is required.

### Migration notes

None required. Existing code continues to work unchanged. Consumers who want link extraction add one import and one `extract` call. Consumers who want reachability checking opt in by passing `{ followExternal: true }` and must be on Node.js, which is enforced by the `pdf-parse/node` export condition rather than a runtime check.