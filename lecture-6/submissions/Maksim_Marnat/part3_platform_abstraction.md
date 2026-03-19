# Part 3.2: Platform Abstraction (Node vs Browser)

## Packages

- `pdf-parse` — core
- `pdf-parse/node` — Node
- `pdf-parse/browser` — browser

## Core (shared)

- `getText`, `getInfo`, `getImages`, `getTables`, `getScreenshots`
- Lifecycle: `open` / `close`

## Node-only

- `getHeader(url, validate?)` — `pdf-parse/node`, `INodePDFUtils`.

## Imports

```ts
import { createParser } from "pdf-parse/browser";

import { createParser, nodeUtils } from "pdf-parse/node";
await nodeUtils.getHeader("https://example.com/doc.pdf", true);
```
