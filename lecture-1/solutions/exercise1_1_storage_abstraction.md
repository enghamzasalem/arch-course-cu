# Exercise 1.1 — Storage Abstraction

Summary

- Implemented an abstract `Storage` interface and two implementations:
  - `FileSystemStorage` — stores files under `data/`
  - `InMemoryStorage` — simple dict-backed storage for testing

Design notes

- The `DocumentManager` depends on the `Storage` interface, not concrete classes.
- This enables dependency injection and swapping providers with zero changes to `DocumentManager`.

How abstraction helps

- Decouples usage from implementation, enabling test doubles.
- Makes vendor substitution (e.g., cloud storage) straightforward.
- Encourages clear, minimal interfaces for the behaviors your system needs.

Usage

- Run the demo: `python lecture-1/solutions/exercise1_1_storage_abstraction.py` (creates `data/` when using filesystem storage)
