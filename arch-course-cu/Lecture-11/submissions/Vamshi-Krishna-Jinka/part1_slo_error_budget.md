# Part 1: Services Map & SLOs
## Task 1.2: SLI / SLO / Error Budget

## 1. User Journey

### Selected Journey: Place Paid Order (Checkout)

This is the most critical user journey for CityBite because it directly affects revenue and user trust. The flow includes:
- User selects items
- Submits order
- Payment is processed
- Order is stored and confirmed

If this journey fails, the user experience is broken and revenue is lost.

---

## 2. Service Level Indicator (SLI)

### SLI Definition:
**Successful checkout rate**

\[
SLI = \frac{\text{Number of successful paid orders}}{\text{Total checkout attempts}}
\]

### Measurement Source:
- API logs (HTTP status codes for `/orders`)
- Payment success responses
- Database commit success

### Success Criteria:
- HTTP 200 response
- Payment confirmed
- Order successfully written to database

---

## 3. Service Level Objective (SLO)

### SLO Target:
**99.5% successful checkouts over a rolling 30-day period**

This means:
- Out of 1000 checkout attempts, at least 995 must succeed
- Up to 0.5% failures are acceptable within the error budget

---

## 4. Error Budget

### Definition:
Error budget = **100% - SLO**

For this system:
- Error budget = **0.5% per month**

This represents the allowed failure rate without violating the SLO.

---

## 5. Error Budget Policy

### When error budget burn is low:
- Normal operation
- Continue feature development and deployments
- Monitor trends

### When error budget burn is high:
- Slow down or pause new feature releases
- Freeze non-critical deployments
- Focus on reliability improvements
- Investigate root causes (e.g. DB overload, payment failures, retry storms)

### When error budget is exhausted:
- Stop all risky changes
- Prioritize incident resolution
- Improve stability before resuming development

---

## 6. Why Error Budget Matters

The error budget creates a balance between:
- **Reliability (keeping the system stable)**
- **Velocity (shipping new features)**

It ensures that CityBite does not sacrifice user experience for rapid development. If failures increase, the system automatically shifts focus to stability.

---

## 7. Summary

- SLI measures real user success (checkout success rate)
- SLO defines the reliability target (99.5%)
- Error budget controls how much failure is acceptable

This approach makes availability measurable and helps teams make informed decisions about deployments and system reliability.