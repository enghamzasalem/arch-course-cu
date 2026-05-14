## Task 1.2: Redesigned Interface Proposal

### Objective
The goal of this task is to design a cleaner and more reusable interface for the `pdf-parse` library by separating concerns like loading, parsing, and data extraction.

---

## 1. Proposed Modular Design

To improve reusability, I split the system into three main parts:

1. **Data Source Layer** → handles how the PDF is loaded  
2. **Parsing / Session Layer** → represents a working session with a PDF  
3. **Extraction Layer** → handles extracting specific data (text, images, etc.)

This way, each part has a clear responsibility and can be changed independently.

---

## 2. Interface Definitions

### 2.1 IPDFSource (Data Loading)


This is a required interface that describes what the component needs from the environment to work.

```ts
interface IPDFSource {
  load(): Promise<PDFData>;
}
 ```

- **Pre-condition:** Input (URL, Buffer, etc.) must be valid and accessible.
- **Post-condition:** Returns a standardized raw data object.


**Rationale:** 
Achieved through Information Hiding. By working with raw bytes, the parser does not need to know if it is running in Node.js or a Browser.

### 2.2 IPDFSession (Parsing / Session)

Acts as a stateful, active component that manages the lifecycle of the document.

```ts
interface IPDFSession {
 
  init(source: IPDFSource): Promise<void>;
  readonly metadata: Record<string, any>;
  isReady(): boolean;
  close(): Promise<void>; 
}
```
 
- Pre-condition: A valid IPDFSource must be provided.
- Post-condition: PDF is parsed and encapsulated as a "black box".
   
**Rationale:** 
Encapsulates parsing logic and state. Making the session explicit avoids zombie-like states where a component is called before its dependencies are satisfied.
 

### 2.3 IPDFExtractor (Extraction Operations)

Follows the Uniform Access Principle, ensuring facilities are accessible in the same way whether they involve heavy computation or simple storage retrieval.TypeScripttype ExtractOperation = "text" | "image" | "table" | "screenshot";

```ts
interface IPDFExtractor {
 
  extract<T>(session: IPDFSession, operation: ExtractOperation, params?: any): Promise<T>;
}
```

- **Pre-condition:** Session must be initialized and ready.
- **Post-condition:** Returns a specific data projection (T).

**Rationale:** Follows the Small Interfaces Principle. Instead of a monolithic class with many methods, the API stays small, and users only use the operations they need.


### 3. Architecture Benefits

- **Support for Node.js and Browser:**  
  Platform-specific features like `getHeader()` (which only works in Node.js) are moved into a separate `NodePDFSession`. This means browser users only see the basic `IPDFSession` interface and aren’t confused by methods they can’t use.

- **Swappable Implementations:**  
  By using a separate `IScreenshotRenderer` interface, we can easily switch between different implementations. For example, we can use a `CanvasRenderer` in the browser or a `SharpRenderer` in Node.js without changing the main extraction logic.

- **Reduced Coupling:**  
  Each interface has a clear and simple responsibility. Loading the PDF, parsing it, and extracting data are all separated. This makes the system easier to understand and change later.

- **Easy to Use / Predictable API:**  
  Using a single `extract()` method for different operations keeps the API consistent. Developers don’t need to learn many different methods, which makes it easier to use and less confusing.