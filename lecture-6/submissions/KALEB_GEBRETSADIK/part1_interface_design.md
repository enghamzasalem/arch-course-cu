# Part 1: Redesigned Interface Proposal for pdf-parse

## 1. Modular Design Overview
The monolithic class approach in `pdf-parse` limits reusability. By applying the Interface Segregation Principle, we should separate concerns into three core domains:
- **`IPDFSource` (Data Source)**: Abstracting where the data comes from (URL, raw buffer, base64 strings).
- **`IPDFSession` (Parsing Session)**: Maintaining the opened document instance without caring what data is extracted.
- **`IExtractor<T>` (Extraction Operation)**: Pluggable plugins that run against the generic session to retrieve specific formats.

## 2. Interface Definitions and Contracts

### 2.1 The Data Source Interface (`IPDFSource`)
This interface standardizes how raw bytes or pointers enter the library.

```typescript
export interface IPDFSource {
  type: 'url' | 'buffer' | 'base64';
  data: string | Buffer;
  password?: string;
}
```
**Contracts:**
- **Preconditions:** `data` must not be null or empty. If `type` is `'url'`, then `data` must be a valid, reachable HTTP(S) link.
- **Postconditions:** Provides a completely uniform property object that the parser can fetch and load without guessing its origin context.
- **Rationale:** Separating how data is acquired from how it is parsed allows clients to easily wrap custom providers (e.g. AWS S3 links or local file blobs) before feeding it into the main session.

### 2.2 Extractor & Parser Session Interfaces
Instead of the single class housing `getText()`, `getImage()`, and `getHeader()`, we decouple them via a plugin model.

```typescript
// A generic base plugin for extracting data from a live session
export interface IExtractor<ResultType, ParamsType = any> {
  extract(session: IPDFSession, options?: ParamsType): Promise<ResultType>;
}

// The active open document and engine lifecycle
export interface IPDFSession {
  // Opens the document globally using the provided source
  load(source: IPDFSource): Promise<void>;
  
  // Method to invoke any pluggable extractor
  execute<ResultType, ParamsType>(
    extractor: IExtractor<ResultType, ParamsType>, 
    options?: ParamsType
  ): Promise<ResultType>;
  
  // Free up resources to avoid massive memory leaks
  destroy(): void;
}
```
**Contracts:**
- **Preconditions for `execute`:** The user MUST have already successfully awaited `load(source)` so that a document instance is active.
- **Postconditions for `execute`:** Returns explicitly the typed `ResultType` provided by the Extractor, resolving with no side-effects on the underlying session state itself.
- **Rationale:** Moving extraction to the `IExtractor<T>` interface shrinks the core session down simply to lifecycle management (`load` and `destroy`). Adding an extraction (like grabbing tables) won't bloat the main `pdf-parse` dependencies.

## 3. Architecture Benefits
- **Node.js vs Browser Support**: Because the core session is isolated from the operations, we can create a `NodeHeaderExtractor` that implements `IExtractor<any>` and only export it from a Node.js-specific bundle. Browser consumers will never see the HTTP module leak into their front-end build.
- **Swappable Implementations**: If the community wants a faster rendering engine for `getScreenshot()`, a developer can simply write a fast `WASMCanvasExtractor` that adheres to the `IExtractor<Buffer>` interface. The fundamental `IPDFSession` logic doesn't have to be rewritten or re-tested.
- **Reduced Coupling**: The loading mechanisms don't interact directly with extractors. If a client app only needs text (`TextExtractor`), their final webpack/rollup bundle drops everything required for images or screenshots entirely, making everything much more reusable and lightweight.
