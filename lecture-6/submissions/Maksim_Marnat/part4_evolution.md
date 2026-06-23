# Part 4.1: Evolution and Versioning Strategy

## v1 → v2

```js
// v1
pdf(buffer).then((r) => r.text);

// v2
new PDFParse({ data }).getText();
```

## Deprecating v1

1. Compatibility shim for one release window.
2. Runtime warning on legacy entry.
3. Migration guide: `buffer` → `{ data }`; `text` output unchanged in meaning.
4. Remove v1 in next major.

## v2 benefits

- Explicit lifecycle / `destroy` or `close`.
- Constructor options separated from extract operations.

## Backward-compatible change (minor, e.g. v2.5)

```ts
getText(params?: { range?: PageRange; stream?: boolean })
```

`stream: true` → chunked async iterator; omit `stream` → same response as today. Default `stream === false`.

## SemVer

- **MAJOR** — breaking contract changes
- **MINOR** — new optional capabilities
- **PATCH** — fixes without contract change
