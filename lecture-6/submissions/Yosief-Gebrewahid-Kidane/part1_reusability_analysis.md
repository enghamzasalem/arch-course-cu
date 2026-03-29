# Part 1 – Task 1.1  
# Reusability Analysis of pdf-parse

## 1. Overview

The **pdf-parse** library is a JavaScript/TypeScript module used to extract information from PDF documents. It supports multiple environments such as **Node.js**, **browsers**, and **serverless platforms**.

The library provides several methods including:

- `getText()`
- `getInfo()`
- `getScreenshot()`
- `getImage()`
- `getTable()`
- `getHeader()` (Node.js only)
- `destroy()`


---

# 2. Strengths of the Current API

## 2.1 Cross-Platform Support

The library works in multiple environments:

- Node.js
- Browser
- Next.js
- Serverless platforms (AWS Lambda, Cloudflare Workers)

This improves reusability because the same library can be used in different application contexts without modification.

Example:

```
const parser = new PDFParse({ url: "file.pdf" })
await parser.getText()
```



---

## 2.2 Multiple Input Sources

The library supports several input formats:

- URL
- Buffer
- Base64 string

Example:

```
new PDFParse({ url: "file.pdf" })
new PDFParse({ data: buffer })
new PDFParse({ base64: base64String })
```

This flexibility improves reusability because the library can be used in different systems such as:

- web applications
- backend services
- file processing pipelines
- serverless functions

---

## 2.3 Multiple Extraction Capabilities

The library provides several extraction methods.

| Method | Description |
|------|-------------|
| `getText()` | Extract text from the PDF |
| `getInfo()` | Retrieve metadata and page information |
| `getImage()` | Extract embedded images |
| `getTable()` | Extract tabular data |
| `getScreenshot()` | Render PDF pages as images |




---

# 3. Weaknesses of the Current API

Despite its strengths, the API has several limitations that reduce its reusability.

---

## 3.1 Monolithic Class Design

The entire functionality is implemented inside a single class:

```
PDFParse
```

This class is responsible for many tasks:

- loading the PDF
- parsing the document
- extracting text
- extracting images
- rendering screenshots
- managing memory and lifecycle

This design creates **tight coupling** between different responsibilities.

Problems caused by this design:

- Hard to replace individual components
- Difficult to extend functionality
- Violates separation of concerns

Example:

```
new PDFParse({...}).getText()
```



---

## 3.2 Platform-Specific Methods Mixed in Core API

The method:

```
getHeader()
```

is **Node.js only**, but it is included in the same interface as browser-compatible methods.

This can cause confusion because browser users see methods that they cannot use.

Example:

| Method | Platform |
|------|-----------|
| `getText()` | Node + Browser |
| `getImage()` | Node + Browser |
| `getTable()` | Node + Browser |
| `getScreenshot()` | Node + Browser |
| `getHeader()` | Node only |

This reduces **interface clarity and portability**.

---

## 3.3 Unclear Method Contracts

The API documentation does not clearly define:

- preconditions
- postconditions
- error handling behavior

Example method:

```
getText(params?)
```

Some unclear aspects include:

- What happens if the PDF is encrypted?
- What happens if the PDF is corrupted?
- What happens if the file size is very large?

Without clearly defined contracts, it becomes harder for developers to integrate the library safely.

---

## 3.4 Too Many Responsibilities in One Object

The `PDFParse` class currently handles multiple responsibilities:

- file loading
- parsing
- extraction
- rendering
- memory management

This violates the **Single Responsibility Principle**.



---

# 4. Interface Issues

## 4.1 Inconsistent Responsibilities

Some methods perform extraction:

```
getText()
getImage()
getTable()
getScreenshot()
```

Other methods perform system-level operations:

```
destroy()
getHeader()
```

These operations should ideally belong to different components in a modular architecture.

---



# 5. Summary of Reusability Issues


| Issue | Impact |
|------|--------|
| Monolithic class design | Reduces modularity |
| Platform-specific methods in core API | Reduces portability |
| Unclear method contracts | Makes integration harder |
| Multiple responsibilities in one class | Increases coupling |


