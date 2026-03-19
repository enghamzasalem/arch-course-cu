# Part 3.1 – Anomaly Detection Design

## Overview

The system looks at metrics from LLM API requests and tries to spot anything unusual. These “anomalies” help us notice problems like spikes in traffic, slow responses, errors, or unexpected costs.

---

## Anomaly Types

### 1. Request Rate Spike
- **Inputs:** How many API calls each app/user makes per minute.  
- **How we check:** Compare the current rate to a baseline (like the last 5 minutes vs the last 7 days).  
- **Output:** Alert if it’s way higher than normal.

### 2. Latency Degradation
- **Inputs:** Response times from the LLM.  
- **How we check:** Look if recent average latency is bigger than normal (baseline + some margin).  
- **Output:** Alert if requests are taking too long.

### 3. Error Rate Spike
- **Inputs:** Number of failed requests (HTTP 4xx, 5xx, timeouts).  
- **How we check:** Compare current error rate to normal. If it’s much higher than usual, it’s an anomaly.  
- **Output:** Alert so we can fix potential issues.

### 4. Token/Cost Drift
- **Inputs:** Tokens used per request and cost.  
- **How we check:** Compare average tokens/cost to normal historical numbers.  
- **Output:** Alert if usage or cost suddenly jumps.

---

## Design Decision

We do anomaly detection in a **separate service (Anomaly Engine)** and run it in **batch mode** every ~60 seconds instead of in the proxy.  

**Why:**  
- Keeps the proxy fast (users get responses quickly).  
- We don’t need real-time detection for most anomalies.  
- Makes it easier to update detection logic without touching the request path.

---

## Summary

Basically, the system keeps an eye on metrics, compares them to what’s normal, and sends alerts when something looks off. This way, we catch problems early and don’t surprise ourselves with weird spikes in usage or errors.