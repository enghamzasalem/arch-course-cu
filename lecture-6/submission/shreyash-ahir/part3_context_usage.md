# Part 3.1 — Usage in Multiple Contexts

## The Core Principle

Each context (Node.js, browser, CLI, REST API client) uses the same three
interfaces — `IPDFSource`, `IPDFSession`, `IPDFExtractor<T>` — from Part 1.
What differs is only how the session and source are constructed, not how they
are used.  This follows the course principle: the interface is stable; the
implementation is replaceable.

---

## Context 1: Node.js Server

**Scenario:** A document service receives a file path from a queue job, extracts
text and metadata, then stores results in a database.

```typescript
// node-service/parse-job.ts
import { BufferSource }  from 'pdf-parse';
import { PDFSession }    from 'pdf-parse';
import { TextExtractor, InfoExtractor } from 'pdf-parse';
import fs from 'fs/promises';

async function processDocument(filePath: string) {
  // Source: read from disk — Node-specific, but hidden from the rest
  const bytes  = await fs.readFile(filePath);
  const source = new BufferSource(bytes);

  // Session and extractors: identical to every other context
  const session  = new PDFSession();
  const textExt  = new TextExtractor();
  const infoExt  = new InfoExtractor();

  await session.open(source);
  try {
    const text = await textExt.extract(session);
    const info = await infoExt.extract(session);
    await saveToDatabase({ text, info });
  } finally {
    await session.close();   // always release workers
  }
}
```

**What is abstracted:** `fs.readFile` — the file system concern lives only in
the source construction.  The extractor code is identical to the browser version.

---

## Context 2: Browser (File Input)

**Scenario:** A web app lets a user upload a PDF and renders the first page as a
preview alongside the extracted text.

```typescript
// browser/pdf-preview.ts
import { BufferSource }       from 'pdf-parse';
import { PDFSession }         from 'pdf-parse';
import { TextExtractor, ScreenshotExtractor } from 'pdf-parse';

async function handleFileUpload(file: File) {
  // Source: read from browser File API — browser-specific, hidden from rest
  const arrayBuffer = await file.arrayBuffer();
  const source = new BufferSource(new Uint8Array(arrayBuffer));

  // Session and extractors: same interface as Node.js
  const session      = new PDFSession({ worker: '/pdf.worker.js' });
  const textExt      = new TextExtractor();
  const screenshotExt = new ScreenshotExtractor();

  await session.open(source);
  try {
    const [textResult, previewResult] = await Promise.all([
      textExt.extract(session, { pages: [1] }),
      screenshotExt.extract(session, { pages: [1], scale: 1.0 }),
    ]);
    renderPreview(previewResult.screenshots[0]);
    renderText(textResult.pages[0].text);
  } finally {
    await session.close();
  }
}
```

**What is abstracted:** `file.arrayBuffer()` — the browser File API concern is
isolated to source construction.  No `getHeader` or `fs` in scope; the browser
bundle does not include Node-only code.

---

## Context 3: CLI

**Scenario:** A developer uses the command line to extract text from a local PDF.

```bash
# Install
npm install -g pdf-parse-cli

# Extract text from a local file
pdf-parse extract-text report.pdf --pages 1-3 --output report.txt

# Extract from a URL
pdf-parse extract-text https://example.com/doc.pdf

# Get metadata
pdf-parse extract-info report.pdf

# Screenshot page 1 at 2x scale
pdf-parse screenshot report.pdf --pages 1 --scale 2.0 --output page1.png
```

**CLI adapter code (internal, not exposed to callers):**

```typescript
// cli/commands/extract-text.ts
import { createSource }  from 'pdf-parse';
import { PDFSession }    from 'pdf-parse';
import { TextExtractor } from 'pdf-parse';
import fs from 'fs/promises';

async function extractTextCommand(input: string, opts: CLIOptions) {
  // createSource inspects input: if it starts with http it uses URLSource,
  // otherwise it reads from disk and uses BufferSource
  const source  = await createSource(input);
  const session = new PDFSession();
  const extractor = new TextExtractor();

  await session.open(source);
  try {
    const result  = await extractor.extract(session, { pages: opts.pages });
    const output  = result.pages.map(p => p.text).join('\n\n');
    await fs.writeFile(opts.output ?? '/dev/stdout', output, 'utf8');
  } finally {
    await session.close();
  }
}
```

**What is abstracted:** Argument parsing and source construction.  The core
extraction is one line, same as Node.js and browser.

---

## Context 4: REST API Client

**Scenario:** A mobile app calls the REST API from Part 2 to extract text without
bundling the pdf-parse library itself.

```typescript
// mobile-client/pdf-api.ts — no pdf-parse dependency at all
async function extractTextFromPDF(fileUrl: string): Promise<string[]> {
  const response = await fetch('https://api.example.com/api/v1/extract/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: fileUrl }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error.message);
  }

  const result = await response.json();
  return result.pages.map((p: { text: string }) => p.text);
}
```

**What is abstracted:** The entire library.  The mobile client depends only on
the HTTP contract.  It can be rewritten in Swift or Kotlin without any knowledge
of the pdf-parse library.

---

## Summary: What Is the Same Across All Contexts

| | Node.js | Browser | CLI | API client |
|---|---|---|---|---|
| Source interface (`IPDFSource`) | ✓ | ✓ | ✓ | HTTP body |
| Session interface (`IPDFSession`) | ✓ | ✓ | ✓ | Server-side |
| Extractor interface (`IPDFExtractor`) | ✓ | ✓ | ✓ | Server-side |
| Platform-specific adapter | `fs.readFile` | `File.arrayBuffer()` | CLI arg parser | `fetch` |
| Node-only `getHeader` | Opt-in | Never imported | Opt-in | Not exposed |

---

## What Was Avoided to Keep the Core Reusable

- No `process.env` or `require('fs')` in core interfaces
- No browser-specific `window`, `document`, or `FileReader` in core
- No HTTP framework imports in the extraction logic
- `getHeader` is not on `IPDFSession` or `IPDFExtractor<T>`
- Worker path is a constructor option for the session, not a global import
