# Part 4.1 — v1 → v2 Migration and Future Evolution

## The v1 → v2 Change

```javascript
// v1: function-based, single call
const result = await pdf(buffer);
console.log(result.text);       // all pages concatenated

// v2: class-based, stateful session
const parser = new PDFParse({ data: buffer });
const text   = await parser.getText();
await parser.destroy();
```

### What v2 improves for reusability

The function-based v1 API provides no lifecycle control.  There is no way
to reuse a parsed document across multiple extraction calls without re-parsing.
The v2 class introduces a stateful session (`destroy()` signals teardown),
which allows sharing one parse result across `getText()`, `getTable()`, and
`getInfo()` without loading the PDF three times.

This is a meaningful reusability improvement: the instance lifecycle
(construct → use → destroy) maps directly to the `IPDFSession` pattern
proposed in Part 1.

### How to deprecate v1 cleanly

The course advises: *"keep it there forever"* and *"never add something you
do not intend to keep forever."*  Since v1 is already in the wild, removing
it abruptly breaks every caller.  The staged approach:

**Step 1 — Emit a deprecation warning (v2.x patch):**

```javascript
// v1 shim
export function pdf(source, options) {
  console.warn(
    '[pdf-parse] The function API is deprecated and will be removed in v3.0.0. ' +
    'Please migrate to new PDFParse({ ... }). ' +
    'Migration guide: https://docs.pdf-parse.dev/migrate-v1-v2'
  );
  const parser = new PDFParse({ data: source, ...options });
  return parser.getText().then(text => ({ text }))
               .finally(() => parser.destroy());
}
```

**Step 2 — Publish a migration guide** documenting every v1 property and
its v2 equivalent.

**Step 3 — Mark as `@deprecated` in JSDoc / TypeScript types** so editors
show a strikethrough immediately.

**Step 4 — Remove in v3.0.0** (major version bump — callers know it is a
breaking change by the semver convention).

---

## Proposed Backward-Compatible Evolution: v2.5

### Feature: `getText()` with streaming output for large files

**The problem:** For a 500-page PDF, `getText()` loads all text into memory
at once.  This is fine for small documents but causes memory pressure in
server environments processing many concurrent requests.

**The change:**

```typescript
// v2.4 (current) — still works unchanged in v2.5
const result = await parser.getText();
// result: { pages: [{ pageNumber, text }] }

// v2.5 — new optional streaming overload
const stream = await parser.getText({ stream: true });
// stream: AsyncIterable<{ pageNumber: number; text: string }>

for await (const page of stream) {
  await writePageToDatabase(page);
}
```

**What changes:** `getText` gains an optional `options` parameter with a
`stream?: boolean` field.

**What stays compatible:**
- Callers that do not pass `{ stream: true }` get the same return type as
  before (`Promise<TextResult>`).
- The type signature uses an overload so TypeScript's return type inference
  is correct for both calls.
- No existing test breaks.

**What cannot break callers:**
- No existing parameter is removed or renamed.
- The return type for the non-streaming call is identical.
- The new `stream` option is ignored if the caller passes an unknown key
  (it is opt-in).

**Migration notes:** None required.  Callers adopt streaming by adding
`{ stream: true }` when they need it.

---

## Future v3 Consideration: `getLinks()`

```typescript
interface LinkResult {
  links: {
    pageNumber: number;
    url: string;
    followExternal?: boolean;
    resolvedTitle?: string;
  }[];
}

class LinkExtractor implements IPDFExtractor<LinkResult> {
  extract(session: IPDFSession, options?: { followExternal?: boolean }): Promise<LinkResult>;
}
```

Because the redesigned interface from Part 1 uses `IPDFExtractor<T>`,
`LinkExtractor` is simply a new class.  The core interfaces do not change.
No existing clients break.  This is the "easier to add than to remove"
principle in action: the generic `IPDFExtractor<T>` interface was designed
explicitly to absorb new extraction types without requiring a new method
on the session or a version bump of the interface contract.
