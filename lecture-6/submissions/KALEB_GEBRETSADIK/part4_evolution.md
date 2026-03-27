# Part 4: Evolution and Versioning

## 1. Migrating from v1 to v2

The original `pdf-parse` v1 used a simple function-based approach (`pdf(buffer).then(r => r.text)`). While easy to use initially, it suffered from a major architectural drawback: it instantiated a new parser, extracted *all* data at once, and immediately threw away the instance. 

### How to deprecate v1 cleanly
We should not break millions of existing codebases overnight. The deprecation strategy is as follows:
- **Runtime Warning:** In v1.9.0, we add a `console.warn` (using a utility string to ensure it only prints to the console once) stating that `pdf()` is deprecated and will be removed in v3.0, pointing users to the new `PDFSession` class.
- **Under-the-hood Wrapping:** In v2.0, we rewrite the old v1 `pdf(buffer)` function to secretly instantiate the new v2 `PDFSession` behind the scenes, execute the text extractor, call `destroy()`, and return the promise. This ensures a 100% backwards-compatible grace period.
- **Migration Guide:** Create a dedicated `MIGRATING.md` in the GitHub repository showing a clean 1-to-1 code comparison of the old syntax versus the new class syntax.

### Improvements in v2 for Reusability
The shift to a v2 class-based architecture (`PDFSession` + `Extractors`) provides massive reusable advantages:
- **Instance Lifecycle Control:** We call `session.load()` once. From there, we can run `getText()`, `getInfo()`, and `getImage()` sequentially without forcing the CPU to parse the entire PDF binary tree three separate times.
- **Memory Management:** The explicit `session.destroy()` method allows us to manually free up the heavy PDF.js worker memory on demand, which is crucial for preventing limits/crashes on long-running backend Node instances.
- **Configurable Workers:** We can inject custom web worker paths (`new PDFSession({ workerSrc: '...' })`), making the library finally usable in strict sandbox environments like Next.js or edge runtimes without requiring bizarre build-tool patches.

## 2. Future Evolution (v2.5 Proposal)

For a future minor release (v2.5), I propose adding a **streaming extraction API** specifically geared for massive documents, which remains completely backwards compatible.

### Proposal: `TextStreamExtractor`
Instead of pulling a 500-page book into a massive single JavaScript String (which often triggers `V8 heap limit Allocation failed` crashes), we will introduce a new plugin that returns an `AsyncIterator` chunk by chunk.

```typescript
// Proposed usage syntax
const stream = await session.execute(new TextStreamExtractor({ chunkSize: 10 }));
for await (const chunk of stream) {
  response.write(chunk.text); // Write directly to the client
}
```

**Compatibility & Migration Strategy:**
- **What changes:** We add export support for the brand new `TextStreamExtractor` class.
- **What stays strictly compatible:** The existing `TextExtractor` remains exactly the same. Our `IPDFSession.execute` contract still accepts any generic `IExtractor<T>` plugin, so zero breaking changes ever touch the core platform.
- **Migration Notes:** Current users upgrading from v2.0 to v2.5 do not need to rewrite a single line of working code. They only need to read the updated docs and adopt `TextStreamExtractor` if they are dealing with gigabyte-sized PDFs.
