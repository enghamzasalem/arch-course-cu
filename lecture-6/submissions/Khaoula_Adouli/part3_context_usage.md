# Part 3.1: Usage in Multiple Contexts

This document shows how the **redesigned pdf-parse interface** (or the current library used in a consistent way) is used in **Node.js server**, **browser**, **CLI**, and **via the REST API**. The same core operations are used in each context; only construction and configuration differ.

---

## 1. Core Interface (Shared)

Across contexts we assume a single conceptual interface:

- **Create session** from source (URL, Buffer, or base64).
- **Extract:** `getText()`, `getInfo()`, `getImage()`, `getTable()`, `getScreenshot()`.
- **Cleanup:** `destroy()`.

No context-specific methods (e.g. `getHeader`) in this core.

---

## 2. Context 1: Node.js Server

**Scenario:** Parse a PDF from a URL and extract text (e.g. in an Express route or worker).

```javascript
const { PDFParse } = require('pdf-parse');  // or redesigned factory

async function handleParseRequest(req, res) {
  const pdfUrl = req.body?.url || req.query?.url;
  if (!pdfUrl) return res.status(400).json({ error: 'Missing url' });

  const parser = new PDFParse({
    url: pdfUrl,
    verbosity: 0
  });

  try {
    const text = await parser.getText();
    const info = await parser.getInfo();
    parser.destroy();
    res.json({ text, pageCount: info?.numPages });
  } catch (err) {
    parser.destroy();
    res.status(422).json({ error: 'Parse failed', details: err.message });
  }
}
```

**What is abstracted:**
- **Source:** URL is passed in options; the library handles fetching (Node has `fetch` or native HTTP).
- **Worker/lifecycle:** Library manages its internal worker; the server only calls `getText()` / `getInfo()` and `destroy()`.

**What we avoid:** Using Node-only features (e.g. `getHeader`) in this shared flow so the same pattern can be mirrored in other environments.

---

## 3. Context 2: Browser

**Scenario:** User selects a file; parse and show first-page screenshot.

```javascript
import { PDFParse } from 'pdf-parse';  // ESM build for browser

async function onFileSelected(file) {
  const arrayBuffer = await file.arrayBuffer();
  const parser = new PDFParse({
    data: new Uint8Array(arrayBuffer),
    verbosity: 0
  });

  try {
    const [page1] = await parser.getScreenshot({ pages: [1], scale: 1.5 });
    document.getElementById('preview').src = `data:image/png;base64,${page1.data}`;
    const info = await parser.getInfo();
    console.log('Pages:', info.numPages);
  } finally {
    parser.destroy();
  }
}

document.getElementById('file-input').addEventListener('change', (e) => {
  const file = e.target.files?.[0];
  if (file) onFileSelected(file);
});
```

**What is abstracted:**
- **Source:** PDF bytes come from `File`/`ArrayBuffer`; the library receives a binary buffer. No URL or filesystem.
- **Worker:** In browser, the library may use a Web Worker or main-thread implementation; the same `getScreenshot()` / `getInfo()` interface is used.

**What we avoid:** Any Node-only APIs (e.g. `getHeader`, `fs`). The core interface stays browser-compatible.

---

## 4. Context 3: CLI

**Scenario:** Command-line tool: `pdf-parse extract-text input.pdf`.

```javascript
#!/usr/bin/env node
const fs = require('fs');
const { PDFParse } = require('pdf-parse');

async function main() {
  const path = process.argv[2];
  if (!path) {
    console.error('Usage: pdf-parse extract-text <file.pdf>');
    process.exit(1);
  }

  const buffer = fs.readFileSync(path);
  const parser = new PDFParse({ data: buffer });

  try {
    const text = await parser.getText();
    console.log(text);
  } finally {
    parser.destroy();
  }
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
```

**What is abstracted:**
- **Source:** PDF is read from disk via `fs`; the library only sees a Buffer. Same `getText()` as in server/browser.
- **Platform:** CLI runs in Node; only the way the Buffer is obtained (file path) is different.

**What we avoid:** Exposing Node-only options in the CLI’s “extract-text” command so the mental model stays “one PDF in → text out” for all contexts.

---

## 5. Context 4: Client Calling the REST API

**Scenario:** Any client (web, mobile, script) uses the HTTP API instead of the library directly.

```javascript
// Example: browser or Node calling the PDF Parse API
async function extractTextViaAPI(pdfSource) {
  const form = new FormData();
  if (pdfSource.file) {
    form.append('file', pdfSource.file);
  } else if (pdfSource.url) {
    return fetch('https://api.example.com/api/v1/extract/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: pdfSource.url })
    }).then((r) => r.json());
  } else if (pdfSource.base64) {
    return fetch('https://api.example.com/api/v1/extract/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base64: pdfSource.base64 })
    }).then((r) => r.json());
  }

  if (form.has('file')) {
    return fetch('https://api.example.com/api/v1/extract/text', {
      method: 'POST',
      body: form
    }).then((r) => r.json());
  }

  throw new Error('Provide file, url, or base64');
}

// Usage (browser): user upload
const textResult = await extractTextViaAPI({ file: fileInput.files[0] });

// Usage (Node): from URL
const textResult = await extractTextViaAPI({ url: 'https://example.com/doc.pdf' });
```

**What is abstracted:**
- **Execution:** Parsing runs on the server; the client only sends PDF input and gets JSON (text, info, images, etc.). No local PDF engine or worker.
- **Interface:** The API mirrors the library (one endpoint per operation: text, info, images, tables, screenshot); the “core interface” is the same from the client’s perspective.

**What we avoid:** Putting library-specific details (e.g. worker path, Node-only APIs) in the client; the contract is “HTTP request in, JSON out.”

---

## 6. Summary Table

| Context      | PDF input        | Same core interface? | What differs              |
|-------------|------------------|-----------------------|---------------------------|
| Node server | URL or Buffer    | Yes (getText, getInfo, …) | How bytes are obtained (URL fetch vs body) |
| Browser     | File / ArrayBuffer | Yes                   | Worker/config; no Node APIs |
| CLI         | File path → Buffer | Yes                   | Input from filesystem     |
| API client  | HTTP (file/url/base64) | Yes (API mirrors ops) | No local library; call REST |

---

## 7. What We Avoid to Keep the Core Reusable

1. **No Node-only methods in the core:** `getHeader` is not part of the shared usage examples; it is opt-in in Node (see Part 3.2).
2. **No platform-specific options in the core:** Options that only work in Node (e.g. custom worker path) are not required for the basic “create → extract → destroy” flow.
3. **Same operation names everywhere:** getText, getInfo, getImage, getTable, getScreenshot map 1:1 to API endpoints and to library methods, so one mental model fits all contexts.

This keeps the core API reusable across Node, browser, CLI, and API clients, with only construction and configuration differing by context.
