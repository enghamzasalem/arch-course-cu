# Part 2.1 – Compatibility and Versioning

## Change A: Add optional `priority` field

| Aspect | Analysis |
|--------|----------|
| **Breaking?** | No |
| **Justification** | Clients that ignore unknown fields continue working. Clients that parse strictly (reject unknown keys) would break, but typical JSON APIs assume tolerance. |
| **Semver bump** | MINOR |
| **Semantic risk** | Clients that validate against a schema (OpenAPI) may reject unknown fields if configured strictly. Documentation should mark field as optional. |

---

## Change B: Rename `done` → `completed`

| Aspect | Analysis |
|--------|----------|
| **Breaking?** | Yes |
| **Justification** | Existing clients expect `done` field. Removing it and adding `completed` breaks all clients that read or write the field. |
| **Semver bump** | MAJOR |
| **Semantic risk** | Even if both fields are present temporarily, clients that write only `done` will not update `completed`, causing inconsistency. |

---

## Change C: Require `X-Client-Id` header

| Aspect | Analysis |
|--------|----------|
| **Breaking?** | Yes |
| **Justification** | Old clients that do not send the header will receive 400/401 errors. All existing clients must update to add the header. |
| **Semver bump** | MAJOR |
| **Semantic risk** | None beyond the clear breaking change – clients either send header or fail. If header is optional with default, could be MINOR. |

---

## Change D: Reduce `title` max length from 500 to 100

| Aspect | Analysis |
|--------|----------|
| **Breaking?** | Yes |
| **Justification** | Tasks with titles between 101-500 characters that were valid before now cause errors. This changes validation rules. |
| **Semver bump** | MAJOR |
| **Semantic risk** | JSON shape is unchanged, but behavior changes. Clients may receive 400 responses for previously valid data. Hard to detect without testing. |

---

## Change E: Add `POST /tasks/bulk` endpoint

| Aspect | Analysis |
|--------|----------|
| **Breaking?** | No |
| **Justification** | Existing endpoints remain unchanged. New endpoint adds functionality without affecting old clients. |
| **Semver bump** | MINOR |
| **Semantic risk** | None – clients that do not call the new endpoint are unaffected. Clients that call it must understand the new request/response shape. |

---

## Summary Table

| Change | Breaking? | Semver | Main Risk |
|--------|-----------|--------|-----------|
| A – Add optional field | No | MINOR | Strict schema validators |
| B – Rename field | Yes | MAJOR | All existing clients break |
| C – Require header | Yes | MAJOR | All existing clients fail |
| D – Stricter validation | Yes | MAJOR | Previously valid data now errors |
| E – New endpoint | No | MINOR | None for existing clients |