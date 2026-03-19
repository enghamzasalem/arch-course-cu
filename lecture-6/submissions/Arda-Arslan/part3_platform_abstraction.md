# Platform-Specific Functionality Handling

## Chosen Approach

The redesign uses submodule separation:

- `pdf-parse` contains the core API
- `pdf-parse/node` contains Node-specific functionality

This keeps the core API reusable across both Node.js and browser environments.

---

## Core Interface

The core API only includes functionality that works in both environments:

- `getText`
- `getInfo`
- `getImage`
- `getTable`
- `getScreenshot`

These operations are accessed through the shared abstractions `IPDFSource`, `IPDFSession`, and `IPDFExtractor<T>`.

---

## Node-Specific Functionality

Node-only functionality is placed in a separate module:

```ts
// pdf-parse/node
interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<HeaderResult>;
}
```

A Node.js user can import this module when needed:

```ts
import { getHeader } from "pdf-parse/node";
```

---

## Browser Independence

A browser user only depends on the core module and does not import `pdf-parse/node`. This ensures that no Node.js-specific code is required in the browser environment.