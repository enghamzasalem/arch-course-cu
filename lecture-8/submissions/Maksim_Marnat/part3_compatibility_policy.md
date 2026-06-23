# Part 3.1 — Public API compatibility policy

**Scope:** Task Board HTTPS JSON API (`/tasks` family). **Audience:** first-party apps and external partners.

## 1. Additive vs breaking

- **Additive (allowed in MINOR):** new **optional** response fields; new **optional** request fields; new endpoints; new **optional** headers; stricter **documented** validation only if it does not reject payloads previously valid under the same major version and published limits.
- **Breaking (requires MAJOR + migration path):** removing/renaming fields or endpoints; making optional fields required; changing types; **tightening** limits (e.g. shorter max length); new **required** headers; changing error `code` meanings; removing error codes.

## 2. Deprecation

- **Notice:** minimum **180 days** calendar notice for MAJOR removals or endpoint shutdown; announced in **release notes**, **email to registered partner contacts**, and **`Sunset` / `Deprecation`** headers on responses where applicable.
- **Communication:** versioned **changelog** (Markdown) + pinned **OpenAPI** per major.
- **Sunset:** date published in policy and response headers; after sunset, version returns **410 Gone** or **301** to successor per gateway rules.

## 3. Error format stability

- Clients **MUST** branch on stable machine **`error.code`** (e.g. `VALIDATION_ERROR`, `MISSING_CLIENT_ID`).
- **`message`** is diagnostic and **may change** wording/locale without MINOR bump.
- New codes may appear in MINOR; **removing or redefining** a code is **breaking** (MAJOR).

## 4. Partners vs first-party

- **Partners:** longer notice where feasible (**≥180 days**); explicit **allowlist** for breaking windows; support **path-based version** (`/v1`, `/v2`) if headers are impractical.
- **First-party** apps: may consume **beta** endpoints flagged in docs; still subject to same semver for public-stable paths.
