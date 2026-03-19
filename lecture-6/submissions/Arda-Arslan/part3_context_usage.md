# Context Usage of the Redesigned pdf-parse API

## 1. Node.js Server Context

In a Node.js environment, a PDF can be loaded from a URL and processed on the server.

```ts
const source = new UrlPDFSource("https://example.com/file.pdf");

const session = new PDFSession();
await session.open(source);

const extractor = new TextExtractor();
const result = await extractor.extract(session);

console.log(result.text);

await session.close();
```

- What is different: PDF is loaded from a URL in a server environment
- What stays the same: `IPDFSession` and `IPDFExtractor<T>` usage
- What is abstracted: file loading and environment-specific handling

---

## 2. Browser Context

In the browser, a PDF is loaded from a file input and processed using the same session and extractor pattern.

```ts
const file = input.files[0];
const buffer = await file.arrayBuffer();

const source = new BufferPDFSource(buffer);

const session = new PDFSession();
await session.open(source);

const extractor = new ScreenshotExtractor();
const result = await extractor.extract(session);

displayImage(result.image);

await session.close();
```

- What is different: PDF is loaded from a file (ArrayBuffer) in the browser
- What stays the same: same session and extraction pattern
- What is abstracted: browser-specific file handling and worker setup

---

## 3. API Usage Context

Instead of using the library directly, clients can interact with a REST API that internally uses the same redesigned interfaces.

```
POST /api/v1/extract/text
Content-Type: application/json

{
  "url": "https://example.com/file.pdf"
}
```

Response:

```json
{
  "text": "Extracted PDF content..."
}
```

- What is different: interaction happens via HTTP instead of direct library usage
- What stays the same: underlying extraction logic and interface design
- What is abstracted: transport layer and service orchestration

---

## What Was Avoided to Keep the Core API Reusable

- No Node.js-specific APIs (e.g. `fs`, `path`) were used in the core interfaces
- No browser-specific APIs (e.g. `FileReader`, worker setup) were included in `IPDFSession` or `IPDFExtractor<T>`
- Platform-specific functionality such as `getHeader()` was kept out of the core and placed in a separate `pdf-parse/node` module
- Extraction logic was not tied to any specific input type — the same extractor works regardless of how the PDF was loaded