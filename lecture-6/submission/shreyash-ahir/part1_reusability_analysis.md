# Part 1.1 — Reusability Analysis of pdf-parse v2.4.5

## Overview

pdf-parse exposes a single `PDFParse` class that handles source loading,
parsing, and all extraction operations.  The analysis below evaluates the
current API against Chapter 6 principles: small interfaces, information
hiding, minimal dependencies, and stable contracts.

---

## Strengths

**1. Multiple input sources reduce caller friction**  
The constructor accepts a URL string, a `Buffer`, or a base64 string.
A caller does not need to pre-convert their data before using the library —
the library absorbs that complexity.  This is a real reusability win: the
same class works in a fetch-then-parse pipeline, a file-read pipeline, and
a base64-decode pipeline.

**2. Cross-platform deployment support**  
The library runs on Node.js, browser, Next.js, Lambda, and Cloudflare
Workers.  Supporting multiple deployment targets without requiring callers
to install platform-specific adapters is a direct application of the
"self-contained component with minimal dependencies" principle from the
course.

**3. `destroy()` enables lifecycle control**  
Providing an explicit teardown method means the library does not force
callers to rely on garbage collection.  This is especially important in
server environments where memory and PDF.js workers must be managed.

---

## Weaknesses

### W1. Monolithic class violates Small Interface Principle

`PDFParse` provides `getText`, `getInfo`, `getScreenshot`, `getImage`,
`getTable`, and `getHeader` all on one object.  A caller that only needs
`getText` still receives — and depends on — the entire class, including
methods it will never call.  The course states: *"If two components
communicate, they exchange as little information as possible."*
Providing the full surface forces clients to couple to more than they need.

### W2. Platform-specific method mixed into the core class

`getHeader` is documented as Node.js only (uses HTTP range requests).
It lives on the same `PDFParse` class as `getText` and `getTable`, which
work in both Node and browser.  This violates information hiding: a browser
caller is exposed to a method that will either throw or silently fail at
runtime.  The platform constraint is invisible at the type level.

**Concrete observation on `getHeader`:**  
- Pre-condition: must run in Node.js; a URL (not Buffer/base64) must be
  the source.  Neither constraint is enforced by the interface.
- Post-condition: returns HTTP headers of the PDF file.  Completely
  unrelated to PDF content extraction — it should not share an interface
  with `getText`.
- Risk: a browser bundler will include `getHeader` dead code (and its
  Node dependencies) in the browser bundle unless tree-shaking eliminates
  it.

### W3. Constructor mixes source type, credentials, and rendering config

The constructor option bag (`{ url | data, password?, verbosity?, ... }`)
combines three distinct concerns:

- **Source type**: `url` vs `data` (how the PDF is obtained)
- **Security**: `password` (decryption credential)
- **Rendering**: `verbosity`, worker configuration options

These will change for different reasons.  A caller swapping from URL to
Buffer must touch the same object as a caller changing verbosity.  Mixing
them increases coupling and makes the interface harder to extend without
breaking callers.

### W4. Unclear contracts on `getText` and `getImage`

**`getText()`:**  
- Pre-condition: not documented.  Does calling `getText` before the
  source is loaded throw? Return an empty string?
- Post-condition: returns text, but page ordering and whitespace handling
  are unspecified.  Two implementations satisfying this interface could
  return different results for the same PDF.

**`getImage(pageNumber?, imageIndex?)`:**  
- `pageNumber` and `imageIndex` are marked optional, but the behavior
  when both are omitted is underdefined.  Does it return all images?
  The first image?  The contract is ambiguous — a caller cannot write
  reliable code without reading the source.

### W5. No uniform extraction pattern

Each extraction method has its own signature, return type, and parameter
names.  There is no shared pattern (e.g. `extract(operation, params)`).
Adding a new extraction type (e.g. `getLinks`) requires adding a new method
to the class, which is a breaking surface change for any typed interface
built on top of it.

---

## Summary Table

| Issue | Principle Violated | Severity |
|---|---|---|
| Monolithic class | Small Interface | High |
| `getHeader` in core class | Information Hiding / Platform separation | High |
| Mixed constructor concerns | Separation of concerns | Medium |
| Undefined contracts on `getText`, `getImage` | Clear Interfaces | Medium |
| No uniform extraction pattern | Uniform Access / Extensibility | Low–Medium |
