# Part 2.1 — Change classification (A–E)

**Assumption unless stated otherwise:** clients **ignore unknown JSON keys** on read (common for web/mobile); **strict** schema validators or codegen **reject** unknown keys — called out per change.

| # | Breaking for existing clients? | Semver (public API) | Semantic risk (one line) |
|---|-------------------------------|---------------------|---------------------------|
| **A** — optional `priority` in responses | **Non-breaking** if clients ignore unknown fields; **breaking** for validators that forbid extra properties. | **MINOR** (additive response field). | Same JSON “shape” passes lenient parsers but **meaning** of “no priority” vs “default priority” can diverge across clients. |
| **B** — `done` → `completed` | **Breaking**: readers/writers expect `done`; PATCH bodies and models break. | **MAJOR**. | Field name unchanged in DB idea, but **wire contract** changes — silent data loss if one side maps wrong. |
| **C** — required `X-Client-Id` | **Breaking**: all requests without header fail. | **MAJOR**. | Header is transport policy, not body — ops/**routing** must agree or clients get mass 400/401. |
| **D** — `title` max 500 → 100 | **Breaking**: previously valid titles (101–500) now rejected. | **MAJOR** (semantic tightening). | **Syntactically** same field; **business rules** changed — stored tasks may become uneditable without migration. |
| **E** — `POST /tasks/bulk` | **Non-breaking** for callers of existing endpoints only. | **MINOR** (additive surface). | New code paths can hide **partial failure** semantics if clients assume same as single POST. |
