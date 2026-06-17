# Part 3.2: Platform Abstraction (Node vs Browser)

This section explains how platform-specific functionality (for example `getHeader`) is separated from the core API so that the main interface can be reused in both Node.js and browser environments.  
Node users can still access additional features, but those features are not part of the shared interface.

---

## 1. Core vs Platform-Specific Features

| Layer | Functions | Supported platform |
|--------|-----------|-------------------|
| Core | getText, getInfo, getImage, getTable, getScreenshot, destroy | Node + Browser |
| Node extras | getHeader(url, validate?) – HTTP header check, partial download | Node only |

The main interface must behave the same everywhere.  
Platform-specific functionality is added separately and only when required.

---

## 2. Selected Design: Core Package + Optional Extensions

To keep the interface reusable, the design uses a small core module and optional Node extensions.

### 2.1 Core module (`pdf-parse` or `pdf-parse/core`)

The core module contains only cross-platform functionality.

Exports:

- PDFParse (or IPDFSession / IPDFExtractor)
- Methods:
  - getText()
  - getInfo()
  - getImage()
  - getTable()
  - getScreenshot()
  - destroy()

Rules:

- No Node-only APIs
- No filesystem or HTTP dependencies
- Works in browser and Node

Different builds may exist internally, but the public interface is identical.

---

### 2.2 Node extension module (`pdf-parse/node`)

Node-specific features are placed in a separate module.

Example:

```ts
// Core interface
interface IPDFExtractor {
  getText(): Promise<string>;
  getInfo(): Promise<any>;
  getImage(): Promise<any[]>;
  getTable(): Promise<any[]>;
  getScreenshot(): Promise<any[]>;
  destroy(): void;
}

// Node-only extension
interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<any>;
}
```

In Node:

```
PDFParse implements IPDFExtractor + INodePDFUtils
```

In browser:

```
PDFParse implements only IPDFExtractor
```

This means `getHeader` exists only in the Node version.

---

## 3. Alternative: Submodule Import

Another safe approach is using a separate import path.

Core usage:

```js
import { PDFParse } from "pdf-parse";
```

Node-only usage:

```js
import { getHeader } from "pdf-parse/node";
```

Benefits:

- Core stays clean
- Node utilities are explicit
- Browser never loads Node code

---

## 4. Browser Safety

The browser build must never depend on Node features.

To ensure this:

1. Separate browser build is provided
2. Bundlers resolve the browser version automatically
3. Node modules like fs / http are not included
4. Types for browser do not contain getHeader

Example rule in package.json:

```
"browser": {
  "./node": false
}
```

Because of this, browser users cannot accidentally call Node-only functions.

---

## 5. Node Opt-In Behavior

Node users can still use extended features.

Example:

```js
const { PDFParse } = require("pdf-parse");
const { getHeader } = require("pdf-parse/node");

const header = await getHeader(url, true);
```

or (extended parser):

```js
const parser = new PDFParse({ url });

if (parser.getHeader) {
  const header = await parser.getHeader(url);
}
```

The extra function exists only in Node.

---

## 6. Summary

| Requirement | Solution |
|------------|----------|
| Same interface everywhere | Core module with shared methods |
| Node-only feature support | Separate module or capability interface |
| Browser compatibility | Browser build without Node APIs |
| Optional Node features | Explicit import or extended interface |

This design keeps the API simple while still allowing platform-specific behavior.

---

## 7. Advantages of This Design

- Core API stays small and stable
- Platform code is isolated
- Browser bundle remains lightweight
- Future extensions can be added safely

For example:

- Node streaming support can be added later
- Browser canvas rendering can be added later
- Core interface does not change

Because of this separation, the library remains reusable across all environments.