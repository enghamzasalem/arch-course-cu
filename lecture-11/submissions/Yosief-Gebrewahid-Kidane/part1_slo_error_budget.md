# Part 1 — SLI, SLO, and Error Budget (CityBite)

## 1. Overview

To maintain a reliable food delivery platform, CityBite must define measurable availability goals instead of relying only on general uptime assumptions. Service Level Indicators (SLIs) and Service Level Objectives (SLOs) help the engineering team understand how the system performs from the user’s perspective and when reliability problems become unacceptable.

This section focuses on the critical user journey of placing a paid order.

---

## 2. Selected User Journey

### User Journey:
**Customer places a paid order successfully**

This workflow includes:
1. Submitting the order request
2. Processing payment
3. Writing the order to PostgreSQL
4. Returning a successful confirmation response

This is one of the most important business-critical flows because failed checkouts directly impact revenue and customer trust.

---

## 3. Service Level Indicator (SLI)

### SLI Definition

The primary SLI for CityBite is:

> Percentage of successful paid checkout requests completed within 2 seconds.

---

### Formula

```text
Successful checkouts under 2s
-----------------------------------------
Total checkout attempts
```

Measurement Sources

The SLI (Service Level Indicator) for CityBite checkout reliability can be measured using:

- API gateway metrics  
- Kubernetes ingress logs  
- Application monitoring dashboards  
- Payment success/failure metrics  

These signals reflect **real user experience**, not just infrastructure uptime.

---

## 4. Service Level Objective (SLO)

### SLO Target

CityBite aims for:

> **99.5% successful paid checkouts per calendar month**

This means:

- Only **0.5% of checkout requests** may fail or exceed the defined latency threshold  
- Reliability is measured based on **user-visible success**, not pod health alone  

---

### Why this SLO matters

Checkout is the most critical user journey in CityBite. Even short outages during peak dinner hours can cause:

- Lost revenue  
- Duplicate or failed orders  
- Customer frustration and reduced trust  
- Increased support load  

This SLO aligns engineering reliability goals with business impact.

---

## 5. Error Budget

### Definition

An error budget defines how much failure is acceptable within the SLO.

For a **99.5% monthly SLO**:

- 0.5% of checkout requests are allowed to fail  
- Small, temporary failures are acceptable within this budget  
- Once the budget is exhausted, reliability becomes the top priority  

---

## 6. High Burn Rate Response

If CityBite consumes its error budget too quickly, the system must slow down risky operations.

### Typical actions:

- Freeze non-essential deployments  
- Pause new feature releases  
- Prioritize incident response and stabilization  
- Investigate root causes of failures  
- Increase monitoring sensitivity and tighten rollback thresholds  

