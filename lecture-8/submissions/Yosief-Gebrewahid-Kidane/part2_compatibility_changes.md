# Part 2.1 — Compatibility and Change Classification

This section reviews each proposed change (A–E) to the API, considering:
- Whether it’s breaking or non-breaking  
- Its impact on semantic versioning (MAJOR / MINOR / PATCH)  
- Potential semantic risks, even if the JSON structure stays the same  

---

## Change A — Add optional field `priority`

### 1. Breaking or Non-breaking
- **Non-breaking**, as long as clients ignore unknown fields  
- Clients that don’t care about extra fields will continue to work normally  

### 2. Semver Recommendation
- **MINOR**  
- Adds functionality without changing existing behavior  

### 3. Semantic Risk
- Strictly validated clients may reject responses with unexpected fields  

---

## Change B — Rename `done` → `completed`

### 1. Breaking or Non-breaking
- **Breaking**  
- Existing clients expect `done` and will fail if it’s removed or renamed  

### 2. Semver Recommendation
- **MAJOR**  
- This directly breaks the API contract and forces client updates  

### 3. Semantic Risk
- Even though the meaning is the same, clients relying on exact field names will break immediately  

---

## Change C — Require header `X-Client-Id`

### 1. Breaking or Non-breaking
- **Breaking**  
- Clients that don’t send this header will have their requests rejected  

### 2. Semver Recommendation
- **MAJOR**  
- Introduces a new required input for all requests  

### 3. Semantic Risk
- Requests that were previously valid now fail, changing expected API behavior  

---

## Change D — Reduce title length (500 → 100)

### 1. Breaking or Non-breaking
- **Breaking (semantic)**  
- Requests that were valid before may now be rejected  

### 2. Semver Recommendation
- **MAJOR**  
- Backward-incompatible change in validation rules  

### 3. Semantic Risk
- The JSON structure stays the same, but the meaning and acceptance rules change, which could cause unexpected failures  

---

## Change E — Add new endpoint `/tasks/bulk`

### 1. Breaking or Non-breaking
- **Non-breaking**  
- Existing endpoints are unaffected  

### 2. Semver Recommendation
- **MINOR**  
- Introduces new functionality without impacting current clients  

### 3. Semantic Risk
- Low risk, but bulk operations could affect performance or consistency if misused  

---

## Summary Table

| Change | Breaking? | Semver | Reason |
|--------|-----------|--------|--------|
| A | No | MINOR | Additive optional field |
| B | Yes | MAJOR | Field rename breaks clients |
| C | Yes | MAJOR | New required header |
| D | Yes | MAJOR | Stricter validation rules |
| E | No | MINOR | New endpoint |