# Anomaly Detection Design

This document describes the anomaly detection strategy used in the LLM API Wrapper system. The goal is to detect abnormal patterns in API usage, performance, and cost.

---

## 1. Request Rate Spike

**Description**  
A sudden increase in the number of API requests within a short time period.

**Inputs**
- Request count per minute
- Historical request rate baseline

**Detection Approach**
A threshold-based rule is used. If the request rate exceeds a predefined limit (for example 3x the normal rate), the system flags this as an anomaly.

**Output**
An alert event is generated and sent to the Alerting System.

---

## 2. Latency Degradation

**Description**  
LLM responses take significantly longer than normal.

**Inputs**
- Request latency metrics
- Average latency baseline

**Detection Approach**
The system compares the current latency to a baseline average. If latency exceeds the acceptable threshold for a sustained period, an anomaly is detected.

**Output**
An alert is sent to notify operators about possible performance degradation.

---

## 3. Error Rate Spike

**Description**  
A sudden increase in failed LLM requests.

**Inputs**
- Number of failed requests
- Error percentage over time

**Detection Approach**
If the percentage of failed requests exceeds a defined threshold (for example 10% of requests), the system identifies this as an anomaly.

**Output**
An alert is generated indicating a potential API outage or integration issue.

---

## 4. Token or Cost Drift

**Description**  
Unexpected increases in token usage or cost per request.

**Inputs**
- Token usage per request
- Estimated cost metrics

**Detection Approach**
The system monitors token usage and compares it with historical averages. If the cost or token count deviates significantly from the baseline, it triggers an anomaly event.

**Output**
An alert is sent to indicate possible misuse, prompt inflation, or abnormal workloads.

---

## Design Decision

The anomaly detection process runs in a **separate Anomaly Detection Service** instead of inside the Proxy Gateway. This design reduces the load on the gateway and allows anomaly detection logic to scale independently.