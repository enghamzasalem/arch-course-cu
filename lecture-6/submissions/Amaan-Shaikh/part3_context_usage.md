# Part 3.1: Usage in Multiple Contexts

This section demonstrates how the redesigned pdf-parse interface can be used in different environments:
Node.js server, browser, command-line tool, and through a REST API.  
The goal is that all environments use the same core operations, while only the setup and input source change.

---

## 1. Shared Core Interface

All contexts rely on the same logical workflow:

- Create a parser session from a source (URL, Buffer, or base64)
- Perform extraction operations:
  - getText()
  - getInfo()
  - getImage()
  - getTable()
  - getScreenshot()
- Release resources using destroy()

The shared interface does not include platform-specific functions such as getHeader.

---

## 2. Context 1: Node.js Server

Example: Server receives a URL and extracts text from the PDF.

```javascript
const { PDFParse } = require('pdf-parse');

async function parseHandler(req, res) {
  const url = req.body?.url;

  if (!url) {
    return res.status(400).json({ error: "URL missing" });
  }

  const parser = new PDFParse({
    url: url,
    verbosity: 0
  });

  try {
    const text = await parser.getText();
    const info = await parser.getInfo();

    parser.destroy();

    res.json({
      text: text,
      pages: info?.numPages
    });

  } catch (e) {
    parser.destroy();
    res.status(422).json({ error: "Parsing failed" });
  }
}
```

Abstracted parts:

- The library handles downloading the PDF.
- The server only calls getText / getInfo.
- Worker management is internal.

Avoided:

- No Node-only utilities in shared logic.

---

## 3. Context 2: Browser

Example: User uploads a file and the first page is rendered as an image.

```javascript
import { PDFParse } from "pdf-parse";

async function handleFile(file) {
  const buffer = await file.arrayBuffer();

  const parser = new PDFParse({
    data: new Uint8Array(buffer)
  });

  try {
    const images = await parser.getScreenshot({
      pages: [1],
      scale: 1.5
    });

    const img = images[0];

    document.getElementById("preview").src =
      "data:image/png;base64," + img.data;

    const info = await parser.getInfo();
    console.log(info.numPages);

  } finally {
    parser.destroy();
  }
}
```

Abstracted parts:

- Browser provides ArrayBuffer instead of file path.
- Library internally decides whether to use worker or main thread.
- Same extraction methods as Node.

Avoided:

- No filesystem access.
- No Node-specific features.

---

## 4. Context 3: CLI Tool

Example: Command line utility reading a PDF file.

```javascript
#!/usr/bin/env node

const fs = require("fs");
const { PDFParse } = require("pdf-parse");

async function run() {

  const filePath = process.argv[2];

  if (!filePath) {
    console.log("Usage: pdf-parse <file.pdf>");
    process.exit(1);
  }

  const data = fs.readFileSync(filePath);

  const parser = new PDFParse({
    data: data
  });

  try {
    const text = await parser.getText();
    console.log(text);
  } finally {
    parser.destroy();
  }
}

run();
```

Abstracted parts:

- CLI reads file using fs.
- Library receives Buffer only.
- Same extraction API.

Avoided:

- No extra options in CLI command.
- Same simple flow as server and browser.

---

## 5. Context 4: REST API Client

Example: Client calls HTTP API instead of using the library.

```javascript
async function extractText(source) {

  if (source.url) {
    return fetch("/api/v1/extract/text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        url: source.url
      })
    }).then(r => r.json());
  }

  if (source.base64) {
    return fetch("/api/v1/extract/text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        base64: source.base64
      })
    }).then(r => r.json());
  }

  if (source.file) {
    const form = new FormData();
    form.append("file", source.file);

    return fetch("/api/v1/extract/text", {
      method: "POST",
      body: form
    }).then(r => r.json());
  }

  throw new Error("No input provided");
}
```

Abstracted parts:

- Client does not use pdf engine locally.
- Server performs parsing.
- API endpoints match library operations.

Avoided:

- No worker config on client.
- No library-specific details.

---

## 6. Comparison

| Context | Input | Same Interface | Difference |
|---------|--------|---------------|------------|
| Node | URL / Buffer | Yes | URL fetch handled by server |
| Browser | File / ArrayBuffer | Yes | No Node APIs |
| CLI | File path | Yes | Uses fs to read |
| API | HTTP request | Yes | Parsing on server |

---

## 7. Reusability Rules Followed

1. Core API stays the same in all environments.
2. Platform features are not required for basic usage.
3. Node-only methods are not included in the core interface.
4. REST API uses same operation names as library.

Because of this, the same design works in Node, browser, CLI, and API without changing the core interface.