##  Task 3.1: Compatibility policy

---

## 1. Additive vs Breaking Changes

**Additive changes** can be released at any time without a version bump and without prior notice. These include adding optional fields to responses, adding new endpoints, and adding new optional query parameters. Clients are expected to ignore fields they do not recognise.

**Breaking changes** require a new major version and may not be applied to an existing version after it has been released. The following are always considered breaking:

- Removing or renaming a field in a request or response
- Adding a required field or header to an existing request
- Tightening validation rules on an existing field (e.g. reducing max length)
- Changing the meaning of an existing field or status code
- Removing an endpoint

If a change is ambiguous, it is treated as breaking by default.

---

## 2. Deprecation Process

When a version or feature is marked for deprecation, the following process applies:

- **Notice period:** A minimum of **6 months** for partner integrations. First-party apps (web SPA, mobile) are given a minimum of **3 months**.
- **Communication:** Deprecation is announced via the developer changelog, direct email to registered partner contacts, and a `Deprecation` response header added to every reply from the affected version. The header includes the planned sunset date.
- **Sunset announcement:** At least **4 weeks before** the sunset date, a final reminder is sent through the same channels. On the sunset date, the deprecated version stops accepting requests and returns `410 Gone` with a message pointing to the current version.

No version is removed without completing all steps above in order.

---

## 3. Error Format Stability

The error response envelope is considered part of the public contract and is subject to the same breaking-change rules as any other response field.

**Stable guarantees:**
- The `error.code` field will always be present on error responses and will not be renamed or removed within a major version.
- Existing error codes will not change their meaning within a major version.
- The `error.message` field is human-readable and is not guaranteed to be stable; clients must not parse or match against it programmatically.

**When codes may change:**
- New error codes may be added at any time (additive).
- Existing codes may be removed or renamed only in a new major version, following the deprecation process.

---

## 4. Partner vs First-Party Treatment

Partner integrations receive a longer notice period (6 months vs 3 months) because their release cycles are external and cannot be coordinated directly. Partners are also notified individually by email and are given a dedicated migration guide for each major version.

First-party apps (web SPA, mobile) are maintained by internal teams and can be updated on a shorter timeline. They receive the same deprecation headers and changelog entries but are not individually contacted.

In both cases, the same API contract applies. Partners do not receive a separate API surface, but they may request an extended sunset window beyond the standard 6 months if migration complexity justifies it. Such extensions are agreed on a case-by-case basis and are time-limited.