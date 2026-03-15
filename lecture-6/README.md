# Lecture 6: Reusability and Interfaces

## Overview

This folder contains practical Python examples and the main assignment for **Chapter 6: Reusability and Interfaces**.

The lecture focuses on designing systems and components for reusability: clear interfaces, abstraction, contracts, API design, and interface evolution.

## Learning Objectives

By working through these materials, you will:

1. **Interface Design Principles** – Minimal, stable, and clear interfaces
2. **Abstraction and Information Hiding** – Expose what is needed, hide implementation
3. **Interface Contracts** – Preconditions, postconditions, invariants
4. **API Design** – Consistency, discoverability, backward compatibility
5. **Library vs Framework** – Who controls the flow (you vs framework)
6. **Component Reusability** – Use the same component in multiple contexts
7. **Interface Evolution** – Optional parameters, deprecation, compatibility
8. **Versioning** – Semantic versioning and compatibility rules

## Example Files

### `example1_interface_design_and_contracts.py`

**Concepts:** Interface design, contracts, API consistency

- Minimal `ICache` interface (get, set, delete)
- Multiple implementations (InMemoryCache, PrefixCache)
- Documented pre/post conditions
- Factory for construction
- Scenario: Caching service

### `example2_reusability_and_versioning.py`

**Concepts:** Library vs framework, evolution, versioning

- Library (ValidationLibrary) vs framework (SimpleEventFramework)
- Interface evolution (ILogger → ILoggerV2 with optional params)
- Deprecation with warnings
- Semantic versioning (ApiVersion, compatibility)
- Reusable JsonSerializer in multiple contexts

## Key Concepts

### Interface Design

- **Minimal**: Only methods that clients need
- **Stable**: Avoid breaking changes; extend with optional parameters
- **Clear**: Consistent naming and semantics across implementations

### Contracts

- **Preconditions**: What must hold before a call
- **Postconditions**: What holds after a successful call
- **Documentation**: Write contracts down and enforce in code where possible

### Library vs Framework

| | Library | Framework |
|---|--------|-----------|
| Control flow | You call it | It calls you |
| Reuse | Functions/classes | Plug-ins, handlers |
| Example | ValidationLibrary | EventFramework |

### Interface Evolution

- Add **optional parameters with defaults** (backward compatible)
- **Deprecate** old methods with warnings, then remove in next major version
- Document **migration path** for callers

### Versioning (Semantic)

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Running the Examples

```bash
cd arch-course-cu/lecture-6
python3 example1_interface_design_and_contracts.py
python3 example2_reusability_and_versioning.py
```

## Assignment

See **`ASSIGNMENT.md`** for the **pdf-parse Redesign** assignment. You will:

- **Analyze** the [pdf-parse](https://www.npmjs.com/package/pdf-parse) npm library for reusability
- **Propose** a redesigned architecture with cleaner interfaces
- **Design how to expose pdf-parse as an HTTP/REST API** – endpoints, request/response format, API architecture
- **Create** API architecture diagram (API layer → service → library)
- **Show** usage in Node.js, browser, CLI, and API client
- **Design** platform abstraction (Node-only features like `getHeader`)
- **Propose** evolution and versioning (v1→v2 migration, future changes)
- **Create** component diagram of the redesigned system

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Chapter 5**: Modularity and Components (interfaces, coupling)
- **Chapter 7**: Composability and Connectors (next lecture)
- **Chapter 3**: Definitions (components and connectors)

## Next Steps

After this lecture you will be able to:

- Design interfaces for reusability
- Document and respect contracts
- Evolve interfaces without breaking callers
- Choose and apply a versioning strategy
