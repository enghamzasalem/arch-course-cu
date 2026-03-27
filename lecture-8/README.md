# Lecture 8: Compatibility and Coupling

## Overview

This folder contains practical Python examples and one assignment for **Chapter 8: Compatibility and Coupling** (Pautasso).

Focus: how dependencies create **coupling**, how **changes propagate**, and how to keep **APIs and components compatible** as they evolve.

**Chapter PDF:** `08_Compatibility_and_Coupling.pdf`

## Learning Objectives

1. **Coupling** — Recognize dependency strength and change ripple
2. **Kinds of coupling** — Data, control, temporal, deployment (conceptual)
3. **Compatibility** — Backward / forward; syntactic vs semantic
4. **Breaking vs non-breaking changes** — Schema and API evolution
5. **Managing dependencies** — Abstractions, layering, dependency direction
6. **Versioning** — Connect to semantic versioning and coexistence (with Lecture 6)

## Example Files

### `example1_compatibility_and_api_evolution.py`

**Concepts:** Compatibility, additive changes, legacy clients, lenient parsing

- Classify example changes (additive vs breaking)
- Optional JSON fields; v1 client reading v2 payloads
- Lenient server parsing older request bodies

### `example2_coupling_and_dependencies.py`

**Concepts:** Tight vs loose coupling, port/adapter

- Service coupled to a concrete dict shape
- Same behavior through `TaskRepository` abstraction

## Running the Examples

```bash
cd arch-course-cu/lecture-8
python3 example1_compatibility_and_api_evolution.py
python3 example2_coupling_and_dependencies.py
```

## Lecture presentation

- **`LECTURE_PRESENTATION.html`** — Open in a browser: **Fullscreen** (`F`), **Save as PDF** (`P` → Print → Save as PDF).
- **`LECTURE_SLIDES_MARP.md`** — Marp source; export to PowerPoint:

  ```bash
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture8.pptx
  ```

## Assignment

See **`ASSIGNMENT.md`**. You will analyze **coupling** and **compatibility** for a multi-client **Task Board API** (design and documentation; no full implementation required).

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Lecture 6:** Reusability and Interfaces
- **Lecture 7:** Composability and Connectors
- **Next:** Later chapters (as listed in your course schedule)

## Next Steps

- Map coupling in realistic architectures
- Plan API evolution with explicit compatibility rules and migration paths
