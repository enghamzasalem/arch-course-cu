# Optional: Interface Stubs for Redesigned pdf-parse

This folder contains minimal **interface definitions** (TypeScript-style pseudocode) to illustrate the redesigned architecture. **Full implementation is not required** by the assignment; these stubs serve as a reference for the design described in `part1_interface_design.md`.

---

## Contents

- **`interfaces.ts`** — Defines:
  - `LoadParameters` and `IPDFSource` (data source)
  - `IPDFParser`, `IPDFSession`, `ExtractOp` (parser/session)
  - `IPDFExtractor` (extraction methods)
  - `INodePDFUtils` (Node-only: getHeader)

You can view the types in any editor; they are not runnable without an implementation.

---

## How this maps to the assignment

| Stub | Part 1 design |
|------|----------------|
| `IPDFSource` + `LoadParameters` | Data source separation |
| `IPDFParser` / `IPDFSession` | Parser session, `extract(op)` |
| `IPDFExtractor` | getText, getInfo, getImage, getTable, getScreenshot |
| `INodePDFUtils` | Platform abstraction (Part 3.2) |

These align with the contracts and rationale in `part1_interface_design.md` and `part3_platform_abstraction.md`.
