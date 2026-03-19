# Part 3: Reusability Across Contexts

## 1. Usage in Multiple Contexts

One of the main goals of the redesigned architecture is to allow `IPDFSession` to remain completely pure and reusable. The only thing that changes across environments is the initial configuration (like where the background worker lives) and the data loading strategy.

### Context 1: Node.js Server
In Node.js, we have access to the filesystem. The core interfaces do not need to know this.

```typescript
import { PDFSession, TextExtractor } from 'pdf-parse-core';
import * as fs from 'fs';

async function extractTextFromLocalFile() {
  const buffer = fs.readFileSync('./assignment.pdf');
  
  // 1. Initialize session (Platform agnostic)
  const session = new PDFSession();
  
  // 2. Load the source
  await session.load({
    type: 'buffer',
    data: buffer
  });

  // 3. Extract using the reusable TextExtractor
  const extractor = new TextExtractor();
  const result = await session.execute(extractor);
  
  console.log("Text extracted:", result.text);
  session.destroy();
}
```

### Context 2: Browser
In the browser, we don't have Node's `fs`, but we can pass a URL or a base64 string from a file input. The `PDFSession` and `TextExtractor` are identical to the Node version.

```javascript
import { PDFSession, TextExtractor } from 'pdf-parse-core';

async function extractTextFromInput(fileInput) {
  // Assume fileInput is an HTML input element with type="file"
  const file = fileInput.files[0];
  const url = URL.createObjectURL(file);

  // 1. Initialize session (We configure the browser worker path here)
  const session = new PDFSession({ workerPath: '/assets/pdf.worker.js' });
  
  // 2. Load the source
  await session.load({
    type: 'url',
    data: url
  });

  // 3. Extract using the identical reusable TextExtractor
  const extractor = new TextExtractor();
  const result = await session.execute(extractor);
  
  console.log("Browser extracted text:", result.text);
  session.destroy();
}
```

### Context 3: API Usage (Client)
A web client calling the REST API we designed in Part 2. The client doesn't need the `pdf-parse-core` library at all, but the API server uses the exact same `PDFSession` behind the scenes.

```javascript
async function fetchPdfText(pdfUrl) {
  const response = await fetch('/api/v1/extract/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source: {
        type: 'url',
        data: pdfUrl
      }
    })
  });
  
  const data = await response.json();
  console.log(data.data.text);
}
```

## 2. Documentation of Abstractions
- **What is abstracted:** The environment. The `PDFSession` doesn't know if it's running in Node or the Browser. The Browser handles worker paths via config during construction, while Node handles it via default local modules. The `type: 'url' | 'buffer'` abstraction keeps file loading completely isolated from parsing.
- **What was avoided:** I strictly avoided putting any conditional `if (isWindow)` or `if (process.env)` logic inside the core session or extractors. That anti-pattern ruins tree-shaking and causes bundler errors.
