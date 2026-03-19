# Evolution and Versioning

## v1 to v2 Migration

The real library changed from a simple function-based API in v1 to a class-based API in v2.

**v1**

```js
pdf(buffer).then(r => console.log(r.text));
```

**v2**

```js
const parser = new PDFParse({ data: buffer });
const result = await parser.getText();
await parser.destroy();
```

### How to deprecate v1 cleanly

A clean migration from v1 to v2 should include:

- a deprecation warning when the old `pdf(buffer)` function is used
- a short migration guide with the old and new usage side by side
- a transition period where v1 still works before removal in the next major version

Example warning:

```
Warning: pdf(buffer) is deprecated. Use new PDFParse({ data: buffer }).getText() instead.
```

This approach helps users migrate without breaking existing code immediately.

### What v2 improves for reusability

v2 improves reusability in several ways:

- It makes the parser lifecycle explicit through creation and cleanup (`new PDFParse(...)` and `destroy()`).
- It supports more configuration through an instance instead of one fixed function call.
- It fits better with the redesigned modular architecture, where loading, session handling, and extraction are separated.
- It is easier to extend for different contexts such as Node.js, browser, and API-based use.

---

## Future Evolution Proposal

A backward-compatible improvement for a future v2.5 is to add an optional `stream` parameter to `TextExtractor` for large PDF files.

```ts
const extractor = new TextExtractor();
await extractor.extract(session, { stream: true });
```

### What changes

- `ExtractOptions` gets one new optional parameter: `stream`
- when `stream: true` is used, text can be processed page by page instead of returning everything at once

### What stays compatible

- existing calls such as `await extractor.extract(session)` still work without any change
- the method name stays the same
- users who do not need streaming can ignore the new option

### Migration note

No migration is required, because this is an optional parameter and does not break existing code.