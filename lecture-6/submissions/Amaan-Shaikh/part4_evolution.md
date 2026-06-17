# Evolution and Versioning

## Migration from v1 to v2

The library originally provided a function-based API in version 1, but version 2 introduced a class-based design.  
This change improves flexibility and makes the library easier to reuse in different environments.

### Version 1

```js
pdf(buffer).then(r => console.log(r.text));
```

### Version 2

```js
const parser = new PDFParse({ data: buffer });

const text = await parser.getText();

await parser.destroy();
```

---

## Clean Deprecation Strategy

When replacing the old API, the transition should not break existing users immediately.  
A proper migration plan should contain the following steps:

1. Show a warning when the old function is used
2. Provide documentation explaining the new API
3. Keep the old API working until the next major release

Example warning message:

```
Deprecated: pdf(buffer) will be removed in the next major version.
Use new PDFParse({ data: buffer }).getText() instead.
```

This allows developers to update their code gradually.

---

## Improvements in Version 2

Version 2 improves reusability and architecture in several ways.

### Explicit lifecycle

The parser is created and destroyed manually.

```
new PDFParse(...)
destroy()
```

This makes resource handling clear and allows reuse of the same parser.

### Better configuration

Options are passed to the constructor instead of a single function call.

This allows:

- different input types
- different parsing settings
- different environments

### Supports modular design

The class-based approach fits better with a modular architecture:

- source loading
- parser session
- extractors

Each part can be replaced or extended.

### Works in multiple environments

The same parser instance can be used in:

- Node.js
- Browser
- CLI
- REST API service

This was harder with the old function API.

---

## Future Evolution Proposal (v2.5)

A safe improvement for a future version is adding streaming support for large files.

Large PDFs may contain many pages, so returning all text at once can use too much memory.

### Proposed change

Add an optional parameter to the text extraction options.

```ts
await parser.getText({
  stream: true
});
```

When enabled, text is processed page by page.

---

## What changes

- A new optional field `stream` is added to the options
- Extraction can return partial results internally
- Memory usage becomes lower for large files

---

## What stays compatible

- Existing calls still work
- Method names do not change
- Default behavior stays the same

Example (still valid):

```ts
await parser.getText();
```

Because the new option is optional, no existing code breaks.

---

## Migration Notes

No migration is required for users.

- Old code continues to work
- New feature can be used only when needed
- Documentation should explain the new option

This keeps the API stable while still allowing the library to evolve.