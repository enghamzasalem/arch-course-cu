The same core interface (`IPDFParser` + `IExtractor<T>`) is used identically in every context. Only construction differs — the source type and `workerSrc` path change to match the platform. No context-specific methods appear in any of the examples below.

---

## Node.js Server

```typescript
import { UrlSource } from "pdf-parse/sources";
import { PDFSession } from "pdf-parse";
import { TextExtractor } from "pdf-parse/extractors";

// Construction: workerSrc resolved from local node_modules
const source  = new UrlSource("https://example.com/report.pdf");
const session = new PDFSession({
  workerSrc: require.resolve("pdfjs-dist/build/pdf.worker.js"),
});

try {
  await session.open(source, { password: "secret" });

  // ── core interface — identical across all contexts ──
  const result = await new TextExtractor().extract(session, { pages: [1, 2] });
  // ───────────────────────────────────────────────────

  console.log(result.text);
} finally {
  await session.close();
  source.dispose();
}
```

**What is abstracted:** The worker is loaded from the local filesystem via `require.resolve`. The caller never touches the PDF.js worker directly.

**What is avoided:** No `fetch`, `FileReader`, or browser APIs. No `getHeader` or any Node-specific method on the core session.

---

## Browser

```typescript
import { Base64Source } from "pdf-parse/sources";
import { PDFSession } from "pdf-parse";
import { ScreenshotExtractor } from "pdf-parse/extractors";
// No import from "pdf-parse/node" — NodeUtils is never bundled

async function handleFileInput(file: File) {
  const base64 = await file.arrayBuffer().then(buf =>
    btoa(String.fromCharCode(...new Uint8Array(buf)))
  );

  // Construction: workerSrc points to a CDN URL
  const source  = new Base64Source(base64);
  const session = new PDFSession({
    workerSrc: "https://cdn.jsdelivr.net/npm/pdfjs-dist/build/pdf.worker.min.js",
  });

  try {
    await session.open(source);

    // ── core interface — identical across all contexts ──
    const pages = await new ScreenshotExtractor().extract(session, {
      pages: [1],
      scale: 1.5,
      format: "png",
    });
    // ───────────────────────────────────────────────────

    const blob = new Blob([pages[0].data], { type: "image/png" });
    document.querySelector("img")!.src = URL.createObjectURL(blob);
  } finally {
    await session.close();
    source.dispose();
  }
}
```

**What is abstracted:** The worker is a CDN URL rather than a local path. `Base64Source` encapsulates the `arrayBuffer` → base64 conversion so the session never sees it.

**What is avoided:** No `fs`, `require.resolve`, or any Node.js API. No Node-only extractor methods. Tree-shaking removes `UrlSource`, `FileSource`, and `NodeUtils` from the bundle entirely because they are never imported.

---

## CLI

```typescript
import { FileSource, UrlSource } from "pdf-parse/sources";
import { PDFSession } from "pdf-parse";
import { TextExtractor } from "pdf-parse/extractors";

const [,, src, ...flags] = process.argv;
const pages = flags.includes("--pages")
  ? flags[flags.indexOf("--pages") + 1].split(",").map(Number)
  : undefined;

// Construction: source type chosen by input format, worker bundled with binary
const source  = src.startsWith("http") ? new UrlSource(src) : new FileSource(src);
const session = new PDFSession({ verbosity: 0 });

try {
  await session.open(source);

  // ── core interface — identical across all contexts ──
  const result = await new TextExtractor().extract(session, { pages });
  // ───────────────────────────────────────────────────

  process.stdout.write(result.text);
} finally {
  await session.close();
  source.dispose();
}
```

Usage:
```
pdf-parse input.pdf
pdf-parse https://example.com/report.pdf --pages 1,2,3
```

**What is abstracted:** Whether the input is a local file or a URL is resolved once at construction; the session and extractor never need to know.

**What is avoided:** No browser APIs. `getHeader` is not used — it could be accessed via `pdf-parse/node` if needed, but it is an explicit opt-in, not part of the core flow.

---

## REST API Client

```python
# Python client — no pdf-parse library installed locally,
# all processing delegated to the API service.
import requests

def extract_text(pdf_path: str, pages: list[int] | None = None) -> str:
    with open(pdf_path, "rb") as f:
        response = requests.post(
            "https://api.example.com/api/v1/extract/text",
            files={"file": (pdf_path, f, "application/pdf")},
            data={"pages": ",".join(map(str, pages))} if pages else {},
            timeout=30,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload["success"]:
        raise RuntimeError(payload["error"]["message"])
    return payload["data"]["text"]

# ── same logical operation as every other context ──
text = extract_text("report.pdf", pages=[1, 2])
# ───────────────────────────────────────────────────
print(text)
```

**What is abstracted:** The PDF processing library is entirely hidden behind the HTTP contract. The client only deals with the response envelope defined in Part 2.1.

**What is avoided:** No PDF.js, no worker configuration, no session lifecycle. The response structure mirrors `TextResult` from the library, so the shape of data is consistent whether you call the library directly or through the API.

---

## Summary

| | Node.js Server | Browser | CLI | REST API Client |
|---|---|---|---|---|
| Source type | `UrlSource` | `Base64Source` | `FileSource` / `UrlSource` | HTTP upload |
| `workerSrc` | `require.resolve(…)` | CDN URL | bundled | N/A |
| Extractor used | `TextExtractor` | `ScreenshotExtractor` | `TextExtractor` | server-side |
| Core interface | `IPDFParser` + `IExtractor<T>` | same | same | HTTP equivalent |
| Node extras used | no | no | no | N/A |

The `TextExtractor` and `ScreenshotExtractor` classes are completely unchanged across Node, browser, and CLI. The only lines that differ between contexts are the two construction lines — source type and `workerSrc`. That is the entire extent of platform-specific code.