# Part 3: Platform Abstraction (Node vs. Browser)

## 1. Chosen Approach: Submodule Export Separation
To solve the issue of Node-specific features (like `getHeader[]` making HTTP range requests) leaking into the browser, the most robust approach is using **Submodules with `package.json` exports**.

Instead of a monolithic export, the package will have a core module and a node-specific submodule.

```json
// In package.json
{
  "name": "pdf-parse",
  "exports": {
    ".": "./dist/core/index.js",
    "./node": "./dist/node/index.js"
  }
}
```

### Core Interface (`pdf-parse`)
This contains the environment-agnostic `IPDFSession`, `TextExtractor`, `ImageExtractor`, etc. This works universally across browsers, React Native, and Node.js.

### Node Interface (`pdf-parse/node`)
This exports everything from the core, plus the Node-specific `HeaderExtractor` and utilities that rely on the Node `http/https/fs` modules.

## 2. How it works in Practice

**How a browser user never depends on Node code:**
A developer writing code for a React frontend will import from the root module:
```javascript
import { PDFSession, TextExtractor } from 'pdf-parse';
```
Since the `HeaderExtractor` only exists in `./dist/node/index.js`, Webpack/Rollup completely ignores it. The browser bundle stays clean, lightweight, and absolutely free of Polyfill warnings (like "Module 'http' not found").

**How a Node user opts in:**
A backend engineer who explicitly needs the `getHeader` range-request optimization will import from the `node` submodule:
```javascript
import { PDFSession } from 'pdf-parse';
import { HeaderExtractor } from 'pdf-parse/node';

const session = new PDFSession();
await session.load({ type: 'url', data: 'http://example.com/file.pdf' });

const header = await session.execute(new HeaderExtractor());
```
Because `HeaderExtractor` implements our generic `IExtractor<T>` interface, the core `PDFSession` executes it flawlessly, even though the core session has no idea it's executing a Node-specific HTTP technique.
