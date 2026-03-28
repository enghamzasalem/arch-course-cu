# Part 3.1: Usage in Multiple Contexts

Core: `IPDFParser` + `IPDFExtractor`. Only source wiring differs.

## Node.js

```ts
import { createParser, NodeUrlSource } from "pdf-parse/node";

const parser = createParser();
const source = new NodeUrlSource();
const bytes = await source.load({ kind: "url", url: "https://example.com/file.pdf" });
const session = await parser.open(bytes, { verbosity: 1 });
const text = await session.extractor().getText({ from: 1, to: 2 });
await session.close();
```

## Browser

```ts
import { createParser, BrowserFileSource } from "pdf-parse/browser";

const parser = createParser();
const source = new BrowserFileSource();
const bytes = await source.load({ kind: "bytes", data: await file.arrayBuffer() });
const session = await parser.open(new Uint8Array(bytes));
const info = await session.extractor().getInfo();
await session.close();
```

## CLI

```bash
pdf-parse extract-text --input ./report.pdf --from 1 --to 3
```

## API client

```bash
curl -X POST https://api.example.com/api/v1/extract/text \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/file.pdf","range":{"from":1,"to":2}}'
```
