## Task 3.1: Usage in Multiple Contexts

The goal of this task was to stop the **platform-leakage** we were seeing in our old code. Previously, our parser would crash in Node because it expected a browser `File` object, or crash in the browser because it tried to use Node’s `fs` module.

I’ve redesigned the API so that the **core logic is identical** regardless of where it’s running. The only thing that changes is how we **initialize** the parser.

---

## 1. The Common Interface (`IPDFParser`)

I started by creating a single “contract.” This ensures that whether a dev is working on the React frontend or the Express backend, they use the exact same methods.

```ts
// This core type works in both Node and Browser
export type PDFSource =
  | { kind: "url"; url: string }
  | { kind: "bytes"; bytes: Uint8Array }; // We use Uint8Array because it's universal

export interface IPDFParser {
  // The methods are the same everywhere
  parse(source: PDFSource): Promise<{ pageCount: number; text: string }>;
  renderPage(source: PDFSource, page: number): Promise<{ image: unknown }>;
}
```

### Why this works

- **Input Normalization:** By using `Uint8Array`, we avoid Node-only `Buffer`s and browser-only `Blob`s.
- **Predictability:** You don’t have to check docs to remember if the method is `extract()` or `parseText()`; it’s always `parse()`.

---

## 2. Usage in Different Contexts

Here is how I implemented the “Same Interface, Different Setup” rule across our three main environments.

---

### Context A: Node.js Server (API Endpoint)

On the server, we usually fetch PDFs from a cloud URL. I built a `createNodePDFParser` factory that handles the Node-specific worker paths.

```ts
import { createNodePDFParser } from "./platform/node";

const parser = createNodePDFParser({
  workerPath: "./dist/pdf.worker.js",
});

// Implementation in a route
app.get("/metadata", async (req, res) => {
  const result = await parser.parse({ kind: "url", url: req.query.path });
  res.json({ pages: result.pageCount });
});
```

---

### Context B: Browser (Frontend Preview)

In the browser, we deal with local file uploads. We just convert the `File` to bytes, and then the rest of the code looks exactly like the Node code above.

```ts
import { createBrowserPDFParser } from "./platform/browser";

const parser = createBrowserPDFParser({
  workerSrc: "/assets/pdf.worker.min.js",
});

// When a user selects a file
const onFileChange = async (file: File) => {
  const bytes = new Uint8Array(await file.arrayBuffer());

  // Notice the 'parse' call is identical to the Node version
  const data = await parser.parse({ kind: "bytes", bytes });
  console.log(`Parsed ${data.pageCount} pages on the client side.`);
};
```

---

### Context C: CLI Tool (Local Scripting)

For our internal CLI tools, we can reuse the Node parser. It reads from the disk and passes the bytes into the same interface.

```ts
const buffer = readFileSync("./input.pdf");
const result = await parser.parse({
  kind: "bytes",
  bytes: new Uint8Array(buffer),
});
```

---

## 3. Key Abstracted Differences

To keep the core clean, I pushed the complicated platform-specific details into adapters.

| Feature | Browser Adapter | Node Adapter |
|---|---|---|
| **Worker Loading** | Loaded via a public URL | Loaded via a local file path |
| **Networking** | Uses standard `fetch` | Uses `node-fetch` or `https` module |
| **Render Output** | Returns a canvas-ready object | Returns a raw image buffer |

---

## 4. Improvements

- **Reusability:** Most of our parsing logic is now in a shared folder and works everywhere.
- **Maintainability:** If we find a bug in text extraction, we fix it once and it’s fixed for Web, Server, and CLI.
- **Separation of Concerns:** The core handles PDF logic; adapters handle environment headaches.

