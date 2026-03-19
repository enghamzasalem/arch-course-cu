# Part 3 – Task 3.2
# Platform Abstraction: Node vs Browser

## 1. Objective

The goal is to **separate Node-specific features** (like `getHeader`) from the core PDF parsing interface so that:

- The **core interface** works in **both Node.js and browser**.
- Node-only methods are **optional**, and browser users **never depend** on Node-specific code.

---

## 2. Core Interface

The **core interface** includes operations available on all platforms:

```ts
interface IPDFExtractor<T> {
    extract(params?: any): Promise<T>
}

interface IPDFParserSession {
    getExtractor<T>(type: "text" | "info" | "image" | "table" | "screenshot"): IPDFExtractor<T>
    close(): Promise<void>
}

interface IPDFParser {
    open(source: IPDFSource): Promise<IPDFParserSession>
}
```

- **Included Methods:** `getText()`, `getInfo()`, `getImage()`, `getTable()`, `getScreenshot()`
- **Platform:** Node.js + Browser
- **Guarantee:** Browser users do not import any Node modules.

---

## 3. Node-Specific Interface

For Node.js only, we define an **optional capability interface**:

```ts
interface INodePDFUtils {
    getHeader(url: string, validate?: boolean): Promise<HTTPHeaderInfo>
}
```

- Can be exported in a **submodule**: `pdf-parse/node`
- Node users can **opt-in** to access this functionality:

```ts
import { PDFParser } from "pdf-parse"
import { NodePDFUtils } from "pdf-parse/node"

const headers = await NodePDFUtils.getHeader("https://example.com/file.pdf")
```

- **Browser users never import `pdf-parse/node`** and thus cannot accidentally call Node-only methods.

---

## 4. Optional Approaches Considered

| Approach | Pros | Cons | Chosen? |
|---------|------|------|---------|
| Submodule (`pdf-parse/node`) | Clean separation, browser-safe | Extra import path | ✅ Yes |
| Optional capability interface (`INodePDFUtils`) | Flexible, interface-based | Users must remember to import | ✅ Yes, combined with submodule |
| Platform detection / conditional export | Auto-detect environment | Harder to tree-shake, may increase bundle size | ❌ No |

**Rationale:**  
- Submodule + optional interface ensures **max reusability**.  
- Browser bundle stays **Node-free**.  
- Node users can **opt in** when they need advanced features like `getHeader`.

---

## 5. Usage Examples

### Browser (No Node Features)

```ts
import { PDFParser, FileSource } from "pdf-parse"

const source = new FileSource(file)
const parser = new PDFParser()
const session = await parser.open(source)
const text = await session.getExtractor("text").extract()
await session.close()
```

- **No Node-specific imports**
- Fully browser-compatible

### Node.js (With Node Features)

```ts
import { PDFParser } from "pdf-parse"
import { NodePDFUtils } from "pdf-parse/node"

const headers = await NodePDFUtils.getHeader("https://example.com/file.pdf")
```

- Node-only code is **opt-in**
- Core PDF parsing remains the same as browser

---

## 6. Summary

- **Core interface**: `getText`, `getInfo`, `getImage`, `getTable`, `getScreenshot` → cross-platform
- **Node-only interface**: `getHeader` → exported via submodule `pdf-parse/node`
- Browser users never depend on Node code → **bundle size remains minimal**
- Node users can opt-in → **flexibility for server-side optimizations**
- Ensures **maximum reusability** across contexts without polluting the core API
