# Part 1.2 — SLI / SLO / Error Budget

## Selected User Journey
"Place a paid order"

---

## SLI (Service Level Indicator)

Percentage of successful order checkouts:

SLI = (Number of successful orders / Total order attempts)

Measured from:
- API logs
- Payment confirmation responses

---

## SLO (Service Level Objective)

Target: **99.5% successful checkouts per month**

This means:
- Out of 1000 attempts → maximum 5 failures allowed

---

## Error Budget

Error Budget = 0.5% failure rate per month

---

## What Happens When Error Budget Is Exceeded

If the system starts failing too often (high burn rate):

- Stop deploying new features
- Focus on fixing reliability issues
- Investigate failures (logs, metrics)
- Reduce risk (disable unstable features)
- Improve monitoring and alerts

---

## Why This Matters

This ensures that:
- The system remains reliable for users
- Engineering decisions are guided by availability targets
- Stability is prioritized over new features when needed