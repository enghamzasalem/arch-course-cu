# Part 2.2 — Version coexistence

## Strategy

**Hybrid:** **`Accept-Version: 1 | 2`** (or `2` default after cutover) on existing paths **`/tasks`**, plus **API Gateway** routes unchanged URLs to **Task API v1** vs **v2** implementation pools. Optional mirror: **`/v1/tasks`** and **`/v2/tasks`** for partners who cannot set headers easily — same handlers, same rules.

## New vs legacy

- **New clients:** send `Accept-Version: 2` (and `X-Client-Id` when policy requires it); use `completed`, new validation, bulk when needed.
- **Legacy:** keep `Accept-Version: 1` (or omit → mapped to v1 during sunset) until deadline; gateway **defaults missing header to v1** only in the transition window, then requires explicit version.

## Operational cost

**Dual deployment:** run **two API variants** (or feature-flagged handlers) + **expanded test matrix** (cross-version regression) + gateway routing table maintenance for the sunset period.
