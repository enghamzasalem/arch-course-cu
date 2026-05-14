## Part 4: Evolution and Versioning

### Task 4.1: v1 → v2 Migration and Future Evolution

This section explains how I would evolve the `pdf-parse` API from **v1** to **v2** in a clean way, without surprising users.  
It also proposes one future improvement for **v2.5 / v3** that stays backward-compatible.

---

## 1. Background: What changed (v1 vs v2)

The real `pdf-parse` API changed from a simple function to a class-based design:

```js
// v1: pdf(buffer).then(r => r.text)
// v2: new PDFParse({ data }).getText()
```

This kind of change can break users if we don’t manage it carefully.

---

## 2. How to deprecate v1 cleanly

### 2.1 Deprecation plan (practical steps)

- **Step 1: Keep v1 working in v2 (as a wrapper)**
  - Export the old v1 function, but implement it using the v2 class internally.
  - This gives existing users time to migrate.

- **Step 2: Add a warning message**
  - When someone calls the v1 function, we print a deprecation warning one time:
    - “`pdf()` is deprecated and will be removed in v3. Use `new PDFParse({ data }).getText()` instead.”

- **Step 3: Write a short migration guide**
  - Include a “before/after” section and common cases (Buffer, URL, file).

- **Step 4: Deprecation timeline**
  - v2.x: v1 still available + warning
  - v3.0: remove v1 export completely

### 2.2 Example migration guide (what users see)

**Old (v1)**

```js
import pdf from "pdf-parse";

const result = await pdf(buffer);
console.log(result.text);
```

**New (v2)**

```js
import { PDFParse } from "pdf-parse";

const parser = new PDFParse({ data: buffer });
const result = await parser.getText();
console.log(result.text);
await parser.destroy();
```

---

## 3. What v2 improves for reusability

### 3.1 Instance lifecycle (cleaner control)

With a class instance, the parser can manage resources better:
- It can cache loaded PDF data across calls (ex: text + metadata)
- It can keep worker state (instead of re-creating it every function call)
- It can provide `destroy()` to clean up memory/worker when done

### 3.2 Better configuration (more flexible across environments)

v2 can take options at construction time, which makes it easier to reuse in different platforms:
- configurable worker (worker path in Node vs worker URL in browser)
- consistent options for performance tuning (page ranges, timeouts, verbosity)

### 3.3 Cleaner interfaces

Instead of exposing random platform-only methods everywhere, v2 can separate:
- core universal methods (`getText`, `getInfo`)
- platform extras behind submodules (ex: `pdf-parse/node`)

---

## 4. One backward-compatible evolution (v2.5 or v3)

### Proposal: Add optional streaming output to `getText()` for large PDFs (v2.5)

**Problem:**
Some PDFs are huge. Returning one giant text string can:
- use lots of memory
- block the UI (in browsers)
- be slow to process on servers

**Solution:**
Add an optional `stream` mode to `getText()` that gives output in chunks.

#### What changes (API)

- Keep the current method working:
  - `getText()` still returns the same result as before
- Add an optional option:
  - `getText({ stream: true })` returns an async iterator of chunks

Example:

```ts
// Existing usage (still works)
const result = await parser.getText();
console.log(result.text);

// New optional usage (v2.5)
for await (const chunk of parser.getText({ stream: true })) {
  process.stdout.write(chunk);
}
```

#### What stays compatible

- Existing code calling `getText()` with no options still works.
- This is additive: we are not removing or renaming anything.

#### Migration notes

- **No migration needed** unless you want the new feature.
- Best practice for large PDFs:
  - Prefer `stream: true` to avoid building one huge string in memory.

---

## 5. Summary

- v1 to v2 is a breaking change, so we should support a smooth migration:
  - wrapper + warnings + a short guide + a clear timeline
- v2 improves reusability by introducing:
  - a real lifecycle (`destroy()`), consistent configuration, and better separation
- A good next evolution is a backward-compatible **streaming** option for large files
