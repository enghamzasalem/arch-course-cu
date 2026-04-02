# Part 1.2: Redesigned Interface Proposal — pdf-parse


1. Introduction

The current pdf-parse API exposes most functionality through a single class (PDFParse) that is responsible for multiple concerns, including loading the PDF, managing the parsing lifecycle, and performing extraction operations. While this design is functional, it introduces tight coupling between responsibilities and reduces long-term reusability.

This redesign proposes a modular architecture that separates the main responsibilities into three independent layers:

- PDF Source Layer – responsible for loading the PDF content
- Parser Session Layer – responsible for managing the parsing lifecycle
- Extraction Layer – responsible for extracting information from the parsed PDF

This separation improves:

- Reusability
- Maintainability
- Platform independence (Node.js and browser)
- Extensibility for future features

The redesigned architecture follows the flow:

PDF Source → Parser Session → Extractors

2. Architectural Overview

The redesigned architecture separates concerns as follows:

| Concern           | Responsibility                          | Interface       |
|-------------------|-----------------------------------------|-----------------|
| Data Source       | How the PDF is loaded                   | IPDFSource      |
| Parser / Session  | Manage parsing lifecycle                | IPDFParser, IPDFSession |
| Extraction        | Extract text, images, tables, etc.      | IPDFExtractor   |

Each component has a single responsibility, making the system easier to extend and reuse.
## 2.1 Architecture Flow

The redesigned architecture follows a clear lifecycle when processing a PDF document:

1. A PDF is provided through an `IPDFSource` implementation (URL, Buffer, base64, or file).
2. The `IPDFParser` loads the source and creates an active `IPDFSession`.
3. The `IPDFSession` exposes extraction capabilities defined in `IPDFExtractor`.

The overall processing flow is therefore:

IPDFSource → IPDFParser → IPDFSession → IPDFExtractor

This lifecycle ensures that each stage has a well-defined responsibility and that implementations can be replaced without affecting other layers.
### Interface Relationship Diagram

+-------------+
|  IPDFSource |
+-------------+
        |
        v
+-------------+
|  IPDFParser |
+-------------+
        |
        v
+-------------+
| IPDFSession |
+-------------+
        |
        v
+---------------+
| IPDFExtractor |
+---------------+

3. Interface Definitions

3.1 IPDFSource — PDF Data Source

The IPDFSource interface represents how the PDF content is obtained. The source may be:

- a remote URL
- a binary buffer
- a base64 encoded string
- a file (browser input)

The parser and extractors do not depend on the source implementation.

**Interface Definition**

```ts
interface IPDFSource {
  /**
   * Load the PDF bytes.
   */
  load(): Promise<ArrayBuffer>;
}
```

**Example Implementations**

Possible implementations include:

- URLPDFSource
- BufferPDFSource
- Base64PDFSource
- FilePDFSource (browser)

Example:

```ts
class URLPDFSource implements IPDFSource {
  constructor(private url: string) {}

  async load(): Promise<ArrayBuffer> {
    const response = await fetch(this.url);
    return await response.arrayBuffer();
  }
}
```

**Contract**

_Preconditions_

- The source must reference a valid PDF document.
- The source must be reachable (for URL sources).

_Postconditions_

- `load()` resolves to the raw PDF bytes as an `ArrayBuffer`.

_Error Conditions_

- Invalid URL
- Network failure
- Non-PDF content

**Rationale**

Separating the PDF source allows the system to support multiple input types without modifying the parser or extraction logic.

3.2 IPDFParser — Parser Factory

The IPDFParser interface is responsible for creating a parser session from a source. It acts as a factory that transforms PDF bytes into a session capable of performing extraction operations.

**Interface Definition**

```ts
interface IPDFParser {
  /**
   * Create a parsing session from a PDF source.
   */
  createSession(source: IPDFSource): Promise<IPDFSession>;
}
```

**Contract**

_Preconditions_

- The provided source must return valid PDF bytes.

_Postconditions_

- Returns a valid `IPDFSession` instance capable of running extraction operations.

**Rationale**

The parser is separated from the source so that different PDF engines or parsing implementations can be used without changing the rest of the system.

3.3 IPDFSession — Parsing Session

The `IPDFSession` represents an active session for a single PDF document. It manages the lifecycle of the parsing process and provides extraction capabilities.

The session holds resources such as:

- parsed PDF structures
- rendering workers
- memory buffers

**Interface Definition**

```ts
interface IPDFSession extends IPDFExtractor {
  /**
   * Destroy the session and release resources.
   */
  destroy(): void;
}
```

**Contract**

_Preconditions_

- The session must be created using `IPDFParser.createSession()`.

_Postconditions_

- After calling `destroy()`, the session becomes invalid and cannot be used for further extraction.

**Rationale**

A session clearly defines the lifecycle of parsing a PDF and allows resources to be managed explicitly.

3.4 IPDFExtractor — Extraction Operations

The `IPDFExtractor` interface defines the operations used to extract information from the parsed PDF. The same interface is used in Node.js and browser environments.

**Interface Definition**

```ts
interface IPDFExtractor {
  getText(params?: { pages?: number[] }): Promise<string>;
  getInfo(): Promise<PDFMetadata>;
  getImage(params?: { page?: number }): Promise<EmbeddedImage[]>;
  getTable(params?: { page?: number }): Promise<TableData[]>;
  getScreenshot(params?: { pages?: number[]; scale?: number }): Promise<PageImage[]>;
}
```

**Method Contracts**

`getText()`

_Preconditions_

- The parsing session must be active.

_Postconditions_

- Returns extracted text in UTF-8 format.

`getInfo()`

_Preconditions_

- Session must be initialized.

_Postconditions_

- Returns document metadata such as title, author, page count, and PDF version.

`getImage()`

_Preconditions_

- Session must be initialized.
- Page number must exist.

_Postconditions_

- Returns a list of embedded images found in the PDF.

`getTable()`

_Preconditions_

- Session must be initialized.

_Postconditions_

- Returns structured table data if tables are detected.
- Returns an empty array if no tables are found.

`getScreenshot()`

_Preconditions_

- Session must be initialized.

_Postconditions_

- Returns rendered images of selected pages.

4. Platform-Specific Extensions

Some operations are Node-specific and should not be included in the core interface.

For example:

- `getHeader(url, validate?)`

This method retrieves HTTP headers and magic bytes without downloading the full PDF.

To keep the core platform-independent, Node-specific functionality is exposed through a separate interface.

**Node Extension Interface**

```ts
interface INodePDFUtils {
  getHeader(url: string, validate?: boolean): Promise<HeaderResult>;
}
```

This interface can be implemented in a Node-only module, such as:

- `pdf-parse/node`

Browser users will not depend on this module.

5. Support for Multiple Platforms

The proposed architecture supports both Node.js and browser environments.

| Layer           | Node.js Implementation         | Browser Implementation        |
|-----------------|--------------------------------|------------------------------|
| Source          | URLPDFSource, BufferPDFSource | FilePDFSource, URLPDFSource  |
| Parser          | Node worker                    | Web Worker                   |
| Extractor       | Same interface                 | Same interface               |

This ensures that the core interface remains identical across platforms.

6. Extensibility and Swappable Implementations

The modular design allows components to be replaced without affecting other layers.

**Examples include:**

_Custom Sources_

Developers can add new sources such as:

- cached PDF sources
- cloud storage loaders
- streaming sources

_Custom Extractors_

New extraction operations can be added, for example:

- `getLinks()`
- `getAnnotations()`
- `getForms()`

These can be implemented without modifying the existing parser interface.

_Alternative Rendering Engines_

Different screenshot renderers can be plugged into the system without changing the public API.

7. Benefits of the Proposed Design

The redesigned architecture improves the original API in several ways.

- **Separation of Concerns** – Each component has a clearly defined responsibility.
- **Improved Reusability** – The same interfaces can be reused in Node.js, browser applications, CLI tools, and API services.
- **Platform Independence** – Node-specific features are isolated from the core.
- **Extensibility** – New extractors or sources can be added without breaking existing code.

8. Summary

The redesigned architecture introduces three core abstractions:

| Interface      | Responsibility                                     |
|----------------|-----------------------------------------------------|
| IPDFSource     | Load the PDF content                                |
| IPDFParser     | Create a parsing session                            |
| IPDFSession    | Manage lifecycle and provide extraction             |
| IPDFExtractor  | Extract text, metadata, images, tables, screenshots |

By separating source loading, parsing lifecycle, and extraction operations, the API becomes more modular, reusable, and easier to extend across multiple platforms.

This architecture also prepares the system for future evolution. New extraction operations (such as `getLinks()` or `getAnnotations()`) can be added without modifying the existing interfaces, and alternative PDF engines could implement the same interfaces while preserving compatibility with existing applications.