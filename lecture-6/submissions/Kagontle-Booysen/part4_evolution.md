# Task 4.1 — Evolution and Versioning Strategy
## pdf-parse v1 → v2 → Future

---

## 1. v1 → v2 Migration

### 1.1 What changed

```typescript
// v1 API — function-based, no lifecycle
import pdf from 'pdf-parse';

const data = await pdf(buffer);
console.log(data.text);       // full text, all pages, no options
console.log(data.numpages);   // metadata mixed into same result object

// v2 API — class-based, explicit lifecycle
import { PDFParse } from 'pdf-parse';

const parser = new PDFParse({ data: buffer });
const text   = await parser.getText();
const info   = await parser.getInfo();
await parser.destroy();
```

### 1.2 What v2 improves for reusability

| Concern | v1 | v2 |
|---|---|---|
| **Instance lifecycle** | Stateless function call; native handle created and destroyed on every call | `destroy()` gives the consumer explicit control over when native resources are released |
| **Multiple operations** | Two operations on the same PDF require two full parses | One `new PDFParse(...)` call; `getText()` and `getInfo()` share the same open document |
| **Configurable worker** | Hardcoded worker path | Constructor accepts `worker` path option, enabling deployment to custom environments |
| **Partial extraction** | Always extracts the entire document | Class methods allow future extension with per-method options (e.g. page range) |
| **Error handling** | Single rejected promise; error type undocumented | Class allows `destroy()` in a `finally` block; errors from each method are separately catchable |
| **Testability** | Must mock the entire `pdf` function | Each method can be mocked independently; the class can be subclassed or replaced |

---

## 2. Deprecating v1 Cleanly

### 2.1 Deprecation strategy — three phases

```
Phase 1 (v2.0)  — v1 function still works, emits deprecation warning
Phase 2 (v2.5)  — v1 function removed from default export, only available
                   via 'pdf-parse/legacy'; warning becomes an error in strict mode
Phase 3 (v3.0)  — v1 removed entirely
```

### 2.2 Phase 1 — Runtime deprecation warning (v2.0)

The v1 function export is kept alive but wrapped to emit a `DeprecationWarning`
on first call. This is the Node.js standard mechanism — tools like `node
--trace-deprecation` show the full call stack, making it easy for consumers to
find the call site.

```typescript
// pdf-parse/index.ts  (v2.0 — backwards-compatible entry point)

import { PDFParse } from './PDFParse';

let _warned = false;

/**
 * @deprecated since v2.0 — use `new PDFParse({ data }).getText()` instead.
 * The v1 function API will be removed in v3.0.
 * Migration guide: https://docs.pdf-parse.dev/migration/v1-to-v2
 */
export default function pdf(
  dataBuffer: Buffer,
  options?: Record<string, unknown>
): Promise<{ text: string; numpages: number; info: Record<string, unknown> }> {
  if (!_warned) {
    process.emitWarning(
      'pdf-parse: The v1 function API is deprecated and will be removed in v3.0. ' +
      'Use `new PDFParse({ data })` instead. ' +
      'See https://docs.pdf-parse.dev/migration/v1-to-v2',
      { type: 'DeprecationWarning', code: 'PDF_PARSE_V1_DEPRECATED' }
    );
    _warned = true;
  }

  // Delegate to v2 internally — no duplicate logic
  const parser = new PDFParse({ data: dataBuffer, ...options });
  return Promise.all([parser.getText(), parser.getInfo(), parser.destroy()])
    .then(([text, info]) => ({
      text,
      numpages: info.pageCount,
      info:     info as unknown as Record<string, unknown>,
    }));
}

// v2 class is the primary export
export { PDFParse };
```

### 2.3 JSDoc `@deprecated` annotation

All v1-era exports carry a machine-readable `@deprecated` tag so IDEs show a
strikethrough at the call site before the code is even run:

```typescript
/**
 * @deprecated since 2.0.0 — use {@link PDFParse} class instead.
 * Will be removed in 3.0.0.
 * @see https://docs.pdf-parse.dev/migration/v1-to-v2
 */
export default function pdf(...): Promise<...>;
```

### 2.4 Migration guide (published at `docs.pdf-parse.dev/migration/v1-to-v2`)

**Step-by-step migration from v1 → v2:**

```typescript
// BEFORE (v1)
import pdf from 'pdf-parse';

const result = await pdf(buffer);
console.log(result.text);
console.log(result.numpages);
console.log(result.info.Author);

// AFTER (v2) — equivalent behaviour
import { PDFParse } from 'pdf-parse';

const parser = new PDFParse({ data: buffer });
try {
  const text = await parser.getText();
  const info = await parser.getInfo();
  console.log(text);
  console.log(info.pageCount);   // renamed: numpages → pageCount
  console.log(info.author);      // renamed: info.Author → info.author (camelCase)
} finally {
  await parser.destroy();        // NEW: explicit resource release
}
```

**Breaking changes to document:**

| v1 field | v2 equivalent | Note |
|---|---|---|
| `result.text` | `await parser.getText()` | Now a separate async call |
| `result.numpages` | `info.pageCount` | Renamed; available from `getInfo()` |
| `result.info` | `await parser.getInfo()` | Returns typed `PdfMetadata` object |
| `result.metadata` | `await parser.getInfo()` | Merged into `getInfo()` |
| `result.version` | `info.pdfVersion` | Renamed |

### 2.5 Codemod (automated migration tool)

A codemod script allows teams with large codebases to migrate automatically:

```bash
# Install and run the v1→v2 codemod
npx pdf-parse-codemod v1-to-v2 ./src

# Dry run — shows what would change without writing files
npx pdf-parse-codemod v1-to-v2 ./src --dry-run
```

The codemod handles the common pattern (`pdf(buffer).then(r => r.text)`) and
leaves a `// TODO: add parser.destroy()` comment at each migration site for
the developer to review.

---

## 3. Future Evolution — v2.5 and v3

### 3.1 Proposed v2.5 addition: `getLinks()` with `followExternal` option

**Rationale:** PDFs frequently contain hyperlinks — both internal page anchors
and external URLs. No extraction method currently surfaces them. `getLinks()` is
additive (new method on existing class), backward-compatible (no existing
method changes), and useful across all platforms.

```typescript
// v2.5 — new method on PDFParse class

interface PdfLink {
  page:      number;
  text:      string;          // visible anchor text, if any
  url:       string;          // resolved URL or '#page=N' for internal links
  type:      'internal' | 'external';
  rect:      { x: number; y: number; width: number; height: number };
}

interface GetLinksOptions {
  pages?:          number[];   // default: all pages
  followExternal?: boolean;    // if true, HEAD-request each external URL
                               // to check reachability; default: false
}

class PDFParse {
  // ... existing methods unchanged ...

  /**
   * Extract all hyperlinks from the document.
   *
   * @since 2.5.0
   * @param opts.pages          Page range to scan. Default: all.
   * @param opts.followExternal If true, sends a HEAD request to each external
   *                            URL and adds `reachable: boolean` to each link.
   *                            Requires network access; default false.
   *
   * Preconditions:  parser is open; pages in range 1..pageCount
   * Postconditions: returns PdfLink[]; [] if no links found (never null)
   *
   * @throws {PdfSessionClosedError} if destroy() has been called
   * @throws {PdfParseError}         on document parse failure
   */
  async getLinks(opts?: GetLinksOptions): Promise<PdfLink[]>;
}
```

**Usage example:**

```typescript
const parser = new PDFParse({ url: 'https://example.com/report.pdf' });

// Basic usage — list all links
const links = await parser.getLinks();
links.forEach(l => console.log(l.type, l.url, l.text));

// With reachability check (opt-in network call)
const checkedLinks = await parser.getLinks({ followExternal: true });
const broken = checkedLinks.filter(l => l.type === 'external' && !l.reachable);
console.log(`${broken.length} broken external links`);

await parser.destroy();
```

### 3.2 What changes, what stays compatible

| | Status | Detail |
|---|---|---|
| `getLinks()` method | ✅ New addition | Not present in v2.0–v2.4 |
| All existing methods | ✅ Unchanged | `getText()`, `getInfo()`, `getImage()`, `getTable()`, `getScreenshot()`, `getHeader()` |
| Constructor signature | ✅ Unchanged | No new required options |
| `PdfLink` type | ✅ New type export | Additive; does not replace any existing type |
| `followExternal` default | ✅ Safe default `false` | Opt-in network behaviour; no existing code is affected |

**Semver verdict:** This is a **minor** version bump (`2.4.x → 2.5.0`).
A new public method is added; nothing is removed or changed. All v2.x code
continues to work without modification.

### 3.3 Migration notes for v2.5 adopters

No migration is required — `getLinks()` is purely additive. Existing code
that does not call `getLinks()` is completely unaffected.

For new adopters:

```typescript
// Minimum usage — just import and call
import { PDFParse } from 'pdf-parse'; // requires 2.5.0+

const parser = new PDFParse({ data: buffer });
const links  = await parser.getLinks({ pages: [1, 2] });
await parser.destroy();
```

### 3.4 Proposed v3.0 change: streaming `getText()` for large files

**Rationale:** For very large PDFs (hundreds of pages), buffering the entire
text in memory before returning is inefficient. A streaming option lets callers
process pages as they are extracted rather than waiting for the full result.

This is a **non-breaking addition** when implemented as an optional overload:

```typescript
// v3.0 — optional stream overload for getText()

// Existing signature — unchanged, still works
getText(opts?: TextOptions): Promise<PageText[]>;

// New overload — opt-in streaming
getText(opts: TextOptions & { stream: true }): AsyncIterable<PageText>;

// Usage
for await (const page of parser.getText({ stream: true })) {
  process.stdout.write(`Page ${page.page}: ${page.text}\n`);
}
```

Because the stream overload is only triggered by explicitly passing
`stream: true`, all existing callers that do not pass this option receive the
existing `Promise<PageText[]>` — no behaviour change, no migration needed.

---

## 4. Versioning Strategy Summary

### Semver rules applied to pdf-parse

| Change type | Version bump | Example |
|---|---|---|
| Fix a bug in an existing method | Patch `2.4.x → 2.4.y` | Fix incorrect page count for linearised PDFs |
| Add new optional method or option | Minor `2.4.x → 2.5.0` | Add `getLinks()` |
| Add new optional parameter with safe default | Minor | Add `followExternal?: boolean` |
| Rename a return field | Major `2.x → 3.0` | `numpages` → `pageCount` |
| Remove a method | Major | Remove v1 `pdf()` function |
| Change method return type | Major | Change `getText()` return from `string` to `PageText[]` |

### Deprecation window policy

```
@deprecated annotation added     → version N
Runtime warning emitted           → version N
Legacy path (`/legacy` submodule) → version N+1 (minor)
Method/export removed             → version N+2 (next major)

Minimum real-world time between deprecation and removal: 12 months
```

### Stability tiers

```typescript
/**
 * @stability stable   — semver-protected; deprecation notice before removal
 * @stability beta     — may change in minor releases; documented as unstable
 * @stability internal — not public API; may change any time
 */
```

All exports from `pdf-parse` (core) are `@stability stable`. Node-only exports
from `pdf-parse/node` are `@stability stable` once they reach v2.5. New methods
introduced in minor releases start at `@stability beta` for one full minor cycle
before being promoted to `@stability stable`.
