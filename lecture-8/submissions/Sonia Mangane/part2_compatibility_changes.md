# Task 2.1: Change classification

| Change | Classification | SemVer Bump | Justification |
|--------|---------------|-------------|---------------|
| A: Add optional `priority` | Non-Breaking | MINOR | Adding a field is backwards-compatible as long as clients follow Postel’s Law (ignore unknown fields). |
| B: Rename `done` → `completed` | Breaking | MAJOR | Existing clients expecting the key `done` will fail to find it, likely resulting in null values or UI crashes. |
| C: Require `X-Client-Id` | Breaking | MAJOR | Any request from an older client that does not include this mandatory header will now be rejected by the server. |
| D: Title 500 → 100 chars | Breaking | MAJOR | This is a contract tightening. Payloads that were previously valid now trigger validation errors (400 Bad Request). |
| E: Add `POST /tasks/bulk` | Non-Breaking | MINOR | Adding a new endpoint provides new functionality without altering the behavior or schema of existing endpoints. |


## Recommended SemVer Strategy

We follow Strict Semantic Versioning:

1. MAJOR version when we make incompatible API changes (B, C, D).

2. MINOR version when we add functionality in a backwards-compatible manner (A, E).

3. PATCH version when we make backwards-compatible bug fixes.


## Semantic Risk Analysis

### 1. Change A (Add priority):
 A client might use a strict JSON parser that throws an exception if it encounters any key not explicitly defined in its internal model.

### 2. Change B (Rename field): 
Even if a client uses an alias to handle both names, the data might be misinterpreted if the client logic depends on the specific string literal for mapping.

### 3. Change C (Required header):
Beyond just failing the request, this may break intermediary caches or proxies that are not configured to vary by or allow this specific custom header.

### 4. Change D (Stricter validation):  
Clients that retry failed requests might enter an infinite loop of bad request responses because a title that was perfectly valid during the draft phase is now permanently rejected.

### 5. Change E (Bulk endpoint): 
If both the bulk upload and the single task tool use the same endpoint to talk to the database, a huge bulk upload can cause latency resulting in the application appearing slow or broken.



