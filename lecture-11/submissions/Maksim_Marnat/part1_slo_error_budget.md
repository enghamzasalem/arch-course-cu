# Part 1.2 — SLI, SLO, and error budget (CityBite)

## User journey

**“Place paid order”** — customer confirms cart, payment is authorized or captured, order is accepted by the restaurant queue, and the customer receives an in-app confirmation with order id (happy path within one session).

## SLI (measurable)

**SLI:** Over a rolling 28-day window, the ratio  

\[
\frac{\text{count of successful “place paid order” outcomes}}{\text{count of attempts where user tapped Pay}}
\]

where **success** is recorded server-side as: HTTP 2xx on the checkout aggregate **and** `payment_status ∈ {authorized, captured}` **and** `order_row` inserted with `state = accepted` (audit log correlation id present).

Data sources: Order API structured logs + payment webhook outcomes (same `order_id`), joined in metrics pipeline or event stream.

## SLO (target)

**SLO:** **99.5%** of “place paid order” attempts per calendar month complete successfully as defined by the SLI.

That leaves at most **0.5%** failed attempts—about **1 in 200**—as acceptable **error budget** for planned maintenance, dependency incidents, and deploy regressions combined.

## Error budget — what we do when burn rate is high

**Error budget** is the remaining “allowed” unreliability before we violate the SLO. We track **burn rate** (how fast we consume budget vs. time into the month).

If burn rate is **high** (e.g. multi-window alerts show we will exhaust budget before month end):

1. **Freeze non-critical changes** — stop feature launches that touch checkout or payment adapters; prioritize fixes and rollback.
2. **Freeze risky deploys** — require CAB + canary-only releases for Order API and payment integration; block broad rollouts.
3. **Capacity & dependency focus** — escalate with PSP; tighten circuit breaker thresholds temporarily if needed; scale Order API **only after** confirming DB and PSP are healthy (avoid useless horizontal scale).
4. **Communicate product-side** — status page, in-app banner if systemic; coordinate with support scripts.

If budget is **already exhausted**, we treat checkout as **incident-grade**: executive notification, optional **read-only** catalog mode or queue-only ordering if product agrees—**product decision**, not just ops.
