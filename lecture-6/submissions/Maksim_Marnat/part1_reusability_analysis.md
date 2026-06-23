# Part 1.1: Reusability Analysis of pdf-parse

## Strengths

- Node + browser.
- Inputs: `url`, `data`, `base64`.
- Operations: `getText`, `getInfo`, `getImage`, `getTable`, `getScreenshot`.
- `destroy()` for cleanup.

## Weaknesses

- Single `PDFParse` class: load + parse session + extraction.
- `getHeader` (Node-only) on the same surface as cross-platform methods.
- Wide constructor options without explicit combination contracts.
- Inconsistent request/response patterns across operations.

## Methods (≥3)

### `getText(params?)`

- Missing explicit contract: page range, whitespace normalization, errors.

### `getImage(params?)`

- Heavy responses; no contract on image format and memory limits.

### `getHeader(url, validate?)` (Node-only)

- Useful for remote PDFs; mixed into browser-facing API increases coupling.

## Interface risks

- Load + parse + extract + platform helpers in one object.
- Weak pre/post documentation.
- Class growth makes evolution harder without breaking changes.
