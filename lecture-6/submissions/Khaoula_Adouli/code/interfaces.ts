/**
 * Optional interface stubs for the redesigned pdf-parse architecture.
 * See part1_interface_design.md and part3_platform_abstraction.md.
 * Not a full implementation — for illustration only.
 */

// ---------------------------------------------------------------------------
// Data source: how the PDF is loaded (URL, Buffer, base64)
// ---------------------------------------------------------------------------

export interface LoadParameters {
  url?: string;
  data?: ArrayBuffer | Buffer;
  base64?: string;
  password?: string;
  verbosity?: number;
}

export interface IPDFSource {
  /**
   * Pre: Exactly one of url, data, base64 is set.
   * Post: Returns a Promise resolving to the raw PDF bytes (or stream).
   */
  load(params: LoadParameters): Promise<ArrayBuffer | ReadableStream>;
}

// ---------------------------------------------------------------------------
// Parser session: create session from bytes, run extractions
// ---------------------------------------------------------------------------

export type ExtractOp = 'text' | 'info' | 'image' | 'table' | 'screenshot';

export interface ExtractParams {
  pages?: [number, number];
  page?: number;
  scale?: number;
}

export interface IPDFSession {
  /**
   * Pre: Session not destroyed; op is supported.
   * Post: Returns result for the given operation.
   */
  extract<T>(op: ExtractOp, params?: ExtractParams): Promise<T>;
  destroy(): void;
}

export interface IPDFParser {
  createSession(data: ArrayBuffer | ReadableStream): Promise<IPDFSession>;
  createSessionFromSource?(params: LoadParameters): Promise<IPDFSession>;
}

// ---------------------------------------------------------------------------
// Extractors: same operations in Node and browser (core interface)
// ---------------------------------------------------------------------------

export interface PDFMetadata {
  numPages?: number;
  title?: string;
  author?: string;
  [key: string]: unknown;
}

export interface EmbeddedImage {
  index: number;
  page?: number;
  mimeType: string;
  data: string; // base64 or buffer per platform
}

export interface TableData {
  page?: number;
  rows: unknown[][];
}

export interface PageImage {
  page: number;
  mimeType: string;
  data: string;
}

export interface IPDFExtractor {
  getText(params?: { pages?: [number, number] }): Promise<string>;
  getInfo(): Promise<PDFMetadata>;
  getImage(params?: { page?: number }): Promise<EmbeddedImage[]>;
  getTable(params?: { page?: number }): Promise<TableData[]>;
  getScreenshot(params?: { pages?: number[]; scale?: number }): Promise<PageImage[]>;
  destroy(): void;
}

// ---------------------------------------------------------------------------
// Node-only: getHeader (not in core; opt-in for Node users)
// ---------------------------------------------------------------------------

export interface HeaderResult {
  contentType?: string;
  contentLength?: number;
  magicBytes?: string;
  [key: string]: unknown;
}

export interface INodePDFUtils {
  /**
   * Node only. HTTP range request / headers for URL without full download.
   * Pre: url is a valid HTTP(S) URL.
   * Post: Returns header/metadata for the resource.
   */
  getHeader(url: string, validate?: boolean): Promise<HeaderResult>;
}

// ---------------------------------------------------------------------------
// Combined type for Node build (core + Node extras)
// ---------------------------------------------------------------------------

export type PDFParseNode = IPDFExtractor & INodePDFUtils;
