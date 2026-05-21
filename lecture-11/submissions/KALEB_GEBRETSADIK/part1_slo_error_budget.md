# Part 1.2: SLI / SLO / Error Budget

**User Journey:** Place a paid order.

**SLI (Service Level Indicator):** 
The ratio of successful checkout responses (HTTP 200/201) to the total number of valid POST requests on the `/checkout` endpoint over a 5-minute rolling window, excluding client errors (HTTP 4xx).

**SLO (Service Level Objective):**
99.9% of all valid `/checkout` requests will succeed over a rolling 30-day window.

**Error Budget:**
The error budget is the remaining 0.1% of allowed failures. When the error budget is exhausted or the burn rate exceeds our safety threshold (e.g., burning through the month's budget in a single day):
1. Freeze all non-critical feature deployments.
2. Reallocate engineering resources to focus entirely on stability and reliability.
3. Resume regular deployments only when the error budget recovers.
