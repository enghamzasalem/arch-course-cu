# Task 3.1 — Usage in Multiple Contexts
## pdf-parse v2.4.5 · Redesigned Interface

---

## Overview

The redesigned interface separates loading, parsing, and extraction into three
independent layers (`IPDFSource`, `IPDFParser`, `IExtractor<T>`). This separation
means the **core extraction interface is identical in every context** — only the
construction and configuration differ. The table below summarises what changes
and what stays constant across all four contexts.

| | Node.js Server | Browser | CLI | REST API Client |
|---|---|---|---|---|
| **Source** | `UrlPDFSource` or `FilePDFSource` | `BufferPDFSource` (File API) | `FilePDFSource` | HTTP request to API |
| **Session** | `PDFSession.open()` | `PDFSession.open()` | `PDFSession.open()` | Handled server-side |
| **Extractors** | `TextExtractor`, `TableExtractor` etc. | `TextExtractor`, `MetadataExtractor` etc. | `TextExtractor` etc. | JSON response from API |
| **Renderer** | `PdfJsRenderer` or `PuppeteerRenderer` | `CanvasRenderer` | `PdfJsRenderer` | Handled server-side |
| **Node-only** | `NodeExtractor.getHeader()` | ❌ not available | `NodeExtractor.getHeader()` | Via `/screenshot` endpoint |
| **Core interface changes** | **none** | **none** | **none** | **none** |

**What is always the same:**
- `IPDFSource.load()` — single method, same signature
- `PDFSession.open(source, opts)` — same static factory
- `IExtractor<T>.extract(opts)` — same method, same return contract
- All error types (`PdfLoadError`, `PdfParseError`, etc.)

**What changes per context (construction only):**
- Which `IPDFSource` implementation is instantiated
- Which `IPageRenderer` implementation is injected into `ScreenshotExtractor`
- Whether `pdf-parse/node` is imported (Node and CLI) or not (browser)

### Core lines — identical in every context

The following three lines are **word-for-word identical** across Node.js, browser,
and CLI. Only the single line that constructs the source differs:

```typescript
// ── The ONE line that differs per context ────────────────────────────────

// Node.js server (URL):
const source = new UrlPDFSource('https://example.com/report.pdf');

// Node.js / CLI (from disk):
const source = new FilePDFSource('/path/to/report.pdf');

// Browser (File API):
const source = new BufferPDFSource(new Uint8Array(await file.arrayBuffer()));

// ── Everything below is IDENTICAL in all three contexts ──────────────────

const session = await PDFSession.open(source, { password, verbosity: 0 });
const result  = await new TextExtractor(session).extract({ pages: [1, 2, 3] });
session.destroy();

// result: PageText[] — same type, same shape, regardless of context
```

This is the central reusability guarantee of the redesign: the core interface
never changes; only the source adapter at the construction site changes.

---

## Context 1 — Node.js Server

**Scenario:** An Express server receives a PDF URL via HTTP POST and returns
extracted text and table data as JSON.

**What is abstracted:** The server uses `UrlPDFSource` to fetch the PDF over
HTTP. The `fetch` call, response handling, and byte conversion are hidden behind
`IPDFSource.load()`. The rest of the code — session open, extractor construction,
extract call — is identical to every other context.

**What was avoided:** No `fs.readFile`, no `http.get`, no `require('canvas')`
in the core logic. All I/O is behind the source abstraction; all rendering is
behind the renderer abstraction.

```typescript
// server.ts  (Node.js — Express)
import express from 'express';
import { PDFSession, TextExtractor, TableExtractor } from 'pdf-parse';
import { UrlPDFSource, NodeExtractor } from 'pdf-parse/node';

const app = express();
app.use(express.json());

app.post('/parse', async (req, res) => {
  const { url, pages, password } = req.body;

  // ── Construction: Node-specific source ───────────────────────────────
  const source = new UrlPDFSource(url);

  // ── Core interface: identical to every other context ─────────────────
  let session;
  try {
    session = await PDFSession.open(source, { password, verbosity: 0 });
  } catch (err) {
    if (err instanceof PdfPasswordError) return res.status(422).json({ error: 'PDF_ENCRYPTED' });
    if (err instanceof PdfLoadError)     return res.status(422).json({ error: 'NOT_A_PDF' });
    throw err;
  }

  const textResult = await new TextExtractor(session).extract({ pages });
  const tables     = await new TableExtractor(session).extract({ pages });

  // ── Node-only: getHeader() via pdf-parse/node ─────────────────────────
  // This call does not exist on the core interface — it is only available
  // through NodeExtractor, imported from 'pdf-parse/node'.
  const bookmarks = await new NodeExtractor(session).getHeader();

  session.destroy();

  res.json({
    pageCount: session.pageCount,
    text:      textResult.map(p => p.text).join('\n\n'),
    pages:     textResult,
    tables,
    bookmarks,
  });
});

app.listen(3000);
```

**Key observations:**
- `PDFSession.open()`, `TextExtractor`, `TableExtractor` — identical to browser and CLI
- Only `UrlPDFSource` and `NodeExtractor` are Node-specific imports
- Swapping the source to `FilePDFSource` (reading from disk) requires changing
  one line: `new FilePDFSource('/uploads/report.pdf')` — no other code changes

---

## Context 2 — Browser

**Scenario:** A React web app lets a user select a PDF from their file system,
then displays the first-page text and a screenshot thumbnail.

**What is abstracted:** The browser uses the File API (`FileReader` or
`file.arrayBuffer()`) to get bytes, wraps them in `BufferPDFSource`, and passes
the source to `PDFSession.open()`. The rest of the code — session, extractors,
extract calls — is identical to the Node.js context.

**What was avoided:** No `fs`, no `path`, no Node-specific imports. The browser
bundle never sees `pdf-parse/node`. The `CanvasRenderer` uses the browser's
native canvas API — no peer dependency needed in the browser.

```typescript
// PdfViewer.tsx  (React — browser)
import { PDFSession, TextExtractor, ScreenshotExtractor } from 'pdf-parse';
import { BufferPDFSource, CanvasRenderer } from 'pdf-parse';
// Note: 'pdf-parse/node' is NOT imported — tree-shaken out of browser bundle

async function parsePDF(file: File) {
  // ── Construction: browser-specific source ────────────────────────────
  const buffer = await file.arrayBuffer();
  const source = new BufferPDFSource(new Uint8Array(buffer));

  // ── Core interface: identical to Node.js and CLI ──────────────────────
  const session = await PDFSession.open(source, { verbosity: 0 });

  const textResult = await new TextExtractor(session).extract({ pages: [1] });

  // ── Construction: browser-specific renderer (canvas API) ─────────────
  const screenshot = await new ScreenshotExtractor(session, new CanvasRenderer())
    .extract({ page: 1, scale: 1.5, format: 'png' });

  session.destroy();

  return {
    pageCount:  session.pageCount,
    text:       textResult[0]?.text ?? '',
    thumbnail:  screenshot.data,   // Uint8Array PNG bytes
  };
}

// Usage in React component
function PdfUploader() {
  async function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const result = await parsePDF(file);
    console.log(result.text);
  }

  return <input type="file" accept=".pdf" onChange={handleChange} />;
}
```

**Key observations:**
- `PDFSession.open()`, `TextExtractor`, `ScreenshotExtractor.extract()` — same
  signatures as Node.js context
- The only browser-specific code is `file.arrayBuffer()` (File API) and
  `new CanvasRenderer()` — both are construction-time choices
- `NodeExtractor.getHeader()` is simply absent — the import path makes it
  impossible to call accidentally

---

## Context 3 — CLI

**Scenario:** A command-line tool that accepts a PDF file path and an operation
flag, then writes the result to stdout.

**What is abstracted:** The CLI uses `FilePDFSource` (Node-only) to read from
disk. All extraction is done through the same `IExtractor<T>` interface. The
`commander` flag parsing is the only CLI-specific concern.

**What was avoided:** No special-casing for "CLI mode" anywhere in the core.
The extractor classes have no knowledge that they are being called from a
terminal rather than an HTTP handler.

```typescript
#!/usr/bin/env node
// cli.ts  (Node.js — CLI tool)
import { program } from 'commander';
import { PDFSession, TextExtractor, TableExtractor, MetadataExtractor } from 'pdf-parse';
import { FilePDFSource, NodeExtractor } from 'pdf-parse/node';

program
  .name('pdf-parse')
  .description('Extract content from PDF files');

// ── pdf-parse extract-text input.pdf ─────────────────────────────────────
program
  .command('extract-text <file>')
  .description('Extract plain text from a PDF')
  .option('--pages <pages>', 'Comma-separated page numbers, e.g. 1,2,3')
  .option('--password <password>', 'Decryption password')
  .action(async (file: string, opts) => {
    // ── Construction: CLI-specific source ─────────────────────────────
    const source = new FilePDFSource(file);
    const pages  = opts.pages?.split(',').map(Number);

    // ── Core interface: identical to Node.js server and browser ────────
    const session = await PDFSession.open(source, { password: opts.password });
    const result  = await new TextExtractor(session).extract({ pages });
    session.destroy();

    // CLI-specific: write to stdout
    result.forEach(p => {
      process.stdout.write(`--- Page ${p.page} ---\n${p.text}\n\n`);
    });
  });

// ── pdf-parse extract-tables input.pdf ───────────────────────────────────
program
  .command('extract-tables <file>')
  .description('Extract tables as JSON')
  .option('--pages <pages>', 'Comma-separated page numbers')
  .action(async (file: string, opts) => {
    const source = new FilePDFSource(file);
    const pages  = opts.pages?.split(',').map(Number);

    const session = await PDFSession.open(source);
    const tables  = await new TableExtractor(session).extract({ pages });
    session.destroy();

    process.stdout.write(JSON.stringify(tables, null, 2) + '\n');
  });

// ── pdf-parse info input.pdf ──────────────────────────────────────────────
program
  .command('info <file>')
  .description('Print document metadata and bookmarks')
  .action(async (file: string) => {
    const source    = new FilePDFSource(file);
    const session   = await PDFSession.open(source);
    const metadata  = await new MetadataExtractor(session).extract();
    const bookmarks = await new NodeExtractor(session).getHeader();
    session.destroy();

    process.stdout.write(JSON.stringify({ metadata, bookmarks }, null, 2) + '\n');
  });

program.parse(process.argv);
```

**Shell invocation examples:**

```bash
# Extract text from all pages
$ pdf-parse extract-text report.pdf

# Extract text from specific pages
$ pdf-parse extract-text report.pdf --pages 1,2,3

# Extract text from a password-protected PDF
$ pdf-parse extract-text report.pdf --password secret

# Extract tables as JSON, redirect to file
$ pdf-parse extract-tables financials.pdf --pages 3,4,5 > tables.json

# Print document metadata and bookmarks
$ pdf-parse info report.pdf
```

**Key observations:**
- `PDFSession.open()`, `TextExtractor.extract()`, `TableExtractor.extract()`,
  `MetadataExtractor.extract()` — identical calls to the server and browser
- Only `FilePDFSource` and `NodeExtractor` are CLI-specific
- `commander` argument parsing and `process.stdout.write` are the only
  CLI-specific concerns — they are outside the core interface entirely

---

## Context 4 — REST API Client

**Scenario:** A JavaScript client (browser app, mobile app, or another server)
calls the HTTP API designed in Task 2.1 to extract text without installing the
`pdf-parse` library directly.

**What is abstracted:** The HTTP transport, base64 encoding, and JSON
serialisation are hidden behind a `PdfApiClient` class whose method signatures
mirror the local extractor interface. From the caller's perspective the API is
the same: call a method, receive typed data.

**What was avoided:** No native PDF parsing dependency in the client. No
platform-specific code. Any language or runtime that can make an HTTP request
can use this client pattern.

```typescript
// PdfApiClient.ts  (works in browser, Node.js, or any HTTP-capable runtime)

interface PageText    { page: number; text: string; }
interface PdfMetadata { title?: string; author?: string; pageCount: number; }
interface Table       { page: number; tableIndex: number; rows: number; cols: number; cells: unknown[]; }
interface RenderedPage{ page: number; width: number; height: number; mimeType: string; data: string; }

class PdfApiClient {
  constructor(
    private readonly baseUrl: string,
    private readonly token: string
  ) {}

  private async post<T>(path: string, body: object): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(`[${data.error.code}] ${data.error.message}`);
    return data as T;
  }

  // ── Mirror of TextExtractor.extract() ─────────────────────────────────
  async extractText(
    source: { type: 'url'; value: string } | { type: 'base64'; value: string },
    opts?: { pages?: number[]; password?: string }
  ): Promise<{ pageCount: number; pages: PageText[]; text: string }> {
    return this.post('/api/v1/extract/text', { source, options: opts });
  }

  // ── Mirror of MetadataExtractor.extract() ─────────────────────────────
  async extractInfo(
    source: { type: 'url'; value: string },
    opts?: { password?: string }
  ): Promise<{ metadata: PdfMetadata }> {
    return this.post('/api/v1/extract/info', { source, options: opts });
  }

  // ── Mirror of TableExtractor.extract() ────────────────────────────────
  async extractTables(
    source: { type: 'url'; value: string },
    opts?: { pages?: number[]; password?: string }
  ): Promise<{ tables: Table[] }> {
    return this.post('/api/v1/extract/tables', { source, options: opts });
  }

  // ── Mirror of ScreenshotExtractor.extract() ───────────────────────────
  async screenshot(
    source: { type: 'url'; value: string },
    opts?: { pages?: number[]; scale?: number; format?: 'png' | 'jpeg'; password?: string }
  ): Promise<{ renders: RenderedPage[] }> {
    return this.post('/api/v1/screenshot', { source, options: opts });
  }
}

// ── Usage: browser app calling the REST API ───────────────────────────────
const client = new PdfApiClient('https://api.example.com', 'my-bearer-token');

// Text extraction — same logical call as new TextExtractor(session).extract()
const textResult = await client.extractText(
  { type: 'url', value: 'https://example.com/report.pdf' },
  { pages: [1, 2, 3] }
);
console.log(textResult.text);

// ── Base64 source: browser file upload via API (no library dependency) ────
// This is the most common browser pattern — the user picks a file,
// the browser encodes it to base64, and the API handles the parsing.
async function uploadAndExtract(file: File): Promise<string> {
  // Convert File to base64 string
  const buffer = await file.arrayBuffer();
  const bytes  = new Uint8Array(buffer);
  const b64    = btoa(String.fromCharCode(...bytes));

  // Call the API with base64 source — mirrors BufferPDFSource in local usage
  const result = await client.extractText(
    { type: 'base64', value: b64 },
    { pages: [1, 2, 3] }
  );
  return result.text;
}

// Screenshot — same logical call as new ScreenshotExtractor(session, renderer).extract()
const screenshot = await client.screenshot(
  { type: 'url', value: 'https://example.com/slides.pdf' },
  { pages: [1], scale: 1.5, format: 'png' }
);
const imgBytes = screenshot.renders[0].data; // base64 PNG

// ── Async usage for large files ───────────────────────────────────────────
async function extractLargeFile(pdfUrl: string): Promise<string> {
  const res = await fetch('https://api.example.com/api/v1/extract/text', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer my-bearer-token',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      source: { type: 'url', value: pdfUrl },
      async: true,
    }),
  });

  const { jobId, pollUrl } = await res.json();

  // Poll until complete
  while (true) {
    await new Promise(r => setTimeout(r, 2000));
    const poll = await fetch(pollUrl, {
      headers: { 'Authorization': 'Bearer my-bearer-token' },
    });
    const job = await poll.json();

    if (job.status === 'complete') return job.result.text;
    if (job.status === 'failed')   throw new Error(job.error.message);
  }
}
```

**Key observations:**
- Method signatures on `PdfApiClient` deliberately mirror the local extractor
  interface — `extractText(source, opts)` maps to `TextExtractor.extract(opts)`,
  `screenshot(source, opts)` maps to `ScreenshotExtractor.extract(opts)`
- No `pdf-parse` library dependency — the client can run in any environment
  that supports `fetch`
- The async polling pattern handles large files transparently; the caller
  receives the same result shape regardless of whether the job ran sync or async

---

## How Each Context Uses the Same Core Interface

The following table maps each context to the specific `IExtractor<T>` methods
called and confirms that no context-specific methods appear on the core
interface.

| Operation | Node.js Server | Browser | CLI | REST API Client |
|---|---|---|---|---|
| Extract text | `TextExtractor.extract()` | `TextExtractor.extract()` | `TextExtractor.extract()` | `client.extractText()` |
| Extract metadata | `MetadataExtractor.extract()` | `MetadataExtractor.extract()` | `MetadataExtractor.extract()` | `client.extractInfo()` |
| Extract tables | `TableExtractor.extract()` | `TableExtractor.extract()` | `TableExtractor.extract()` | `client.extractTables()` |
| Render page | `ScreenshotExtractor.extract()` | `ScreenshotExtractor.extract()` | `ScreenshotExtractor.extract()` | `client.screenshot()` |
| Open session | `PDFSession.open(source)` | `PDFSession.open(source)` | `PDFSession.open(source)` | handled server-side |
| Release session | `session.destroy()` | `session.destroy()` | `session.destroy()` | handled server-side |

### What is abstracted per context

| Context | Abstracted behind interface |
|---|---|
| Node.js Server | URL fetching (`UrlPDFSource`), filesystem (`FilePDFSource`), headless rendering (`PuppeteerRenderer`) |
| Browser | `file.arrayBuffer()` File API call (`BufferPDFSource`), canvas rendering (`CanvasRenderer`) |
| CLI | `fs.readFile` filesystem access (`FilePDFSource`), `process.argv` parsing (`commander`) |
| REST API Client | HTTP transport, JSON encoding, base64 encoding, async job polling |

The pattern is consistent across all four contexts: every platform-specific
concern is pushed to the outermost layer — the source constructor or the
renderer constructor — and never leaks into the session or extractor code.
A developer adding a fifth context (e.g. a Deno server or a React Native app)
needs to implement exactly one thing: a new `IPDFSource` that produces bytes
for their platform. The session opens identically, the extractors run
identically, and the results are typed identically.

### What was avoided to keep the core API reusable

| Avoided | Why |
|---|---|
| `require('fs')` in core extractors | Would prevent browser use |
| `require('canvas')` in `ScreenshotExtractor` | Would fail in environments without native canvas addon |
| `process.argv` in any extractor | CLI concern belongs in the CLI layer only |
| `fetch` hardcoded in extractors | Source resolution belongs in `IPDFSource` only |
| Platform checks (`if (typeof window !== 'undefined')`) in extractors | Platform concern belongs in the adapter/source layer only |
| `getHeader()` on the core `IExtractor` interface | Node-only capability belongs in `pdf-parse/node` only |
| Coupled session creation to extraction | Extractors accept an open `IPDFParser` — they never open or close a session themselves |
