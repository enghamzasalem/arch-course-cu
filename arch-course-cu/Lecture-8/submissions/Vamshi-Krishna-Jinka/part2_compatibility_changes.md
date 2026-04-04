# Part 2: Compatibility and Versioning

## Task 2.1: Change Classification

### Objective
Classify API changes based on syntactic and semantic compatibility, and recommend appropriate semantic versioning (semver) updates.

---

## A. Add optional JSON field `priority` to GET /tasks response

- **Breaking or Non-breaking**:  
  Non-breaking (backward compatible)

- **Justification**:  
  This is an additive change. Clients that ignore unknown fields will continue to function without modification.

- **Recommended Semver Bump**:  
  MINOR

- **Semantic Risk**:  
  Clients with strict JSON parsing (rejecting unknown fields) may fail even though the structure is compatible.

---

## B. Rename JSON field `done` → `completed` in responses

- **Breaking or Non-breaking**:  
  Breaking

- **Justification**:  
  This is a structural (syntactic) breaking change since existing clients expect the field `done` and will fail when it is removed or renamed.

- **Recommended Semver Bump**:  
  MAJOR

- **Semantic Risk**:  
  Even if meaning is unchanged, clients relying on the exact field name will break at runtime.

---

## C. Require new header `X-Client-Id` on all requests

- **Breaking or Non-breaking**:  
  Breaking

- **Justification**:  
  Existing clients that do not send this header will receive errors (e.g., 400 or 401), making this a contract-breaking change.

- **Recommended Semver Bump**:  
  MAJOR

- **Semantic Risk**:  
  Clients may appear syntactically correct but fail due to missing required metadata in headers.

---

## D. Change `title` max length from 500 to 100 characters

- **Breaking or Non-breaking**:  
  Breaking (semantic)

- **Justification**:  
  Although the JSON structure remains the same, previously valid inputs (101–500 characters) will now be rejected, making this a semantic breaking change.

- **Recommended Semver Bump**:  
  MAJOR

- **Semantic Risk**:  
  Clients may continue sending valid-looking requests that now fail validation, causing unexpected runtime errors.

---

## E. Add POST `/tasks/bulk` with new request shape

- **Breaking or Non-breaking**:  
  Non-breaking

- **Justification**:  
  This introduces a new endpoint without modifying existing ones, so existing clients are unaffected.

- **Recommended Semver Bump**:  
  MINOR

- **Semantic Risk**:  
  Clients may misuse or misunderstand bulk semantics (e.g., partial success handling) even though existing APIs remain unchanged.

---

## Summary

| Change | Compatibility | Type of Change        | Semver |
|--------|-------------|----------------------|--------|
| A      | Non-breaking | Additive (optional)  | MINOR  |
| B      | Breaking     | Syntactic            | MAJOR  |
| C      | Breaking     | Contract             | MAJOR  |
| D      | Breaking     | Semantic             | MAJOR  |
| E      | Non-breaking | Additive (new API)   | MINOR  |

---

## Key Insight

- **Additive changes** (optional fields, new endpoints) are generally safe  
- **Renaming or removing fields** causes **syntactic breakage**  
- **Validation changes** cause **semantic breakage**, even if JSON shape is unchanged  
- Long-lived clients (e.g., partner integrations) are most vulnerable to breaking changes  

---