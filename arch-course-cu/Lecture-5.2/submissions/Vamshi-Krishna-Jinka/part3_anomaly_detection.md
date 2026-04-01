# Anomaly Detection Design – LLM API Wrapper

## Overview
The LLM API Wrapper monitors requests to external LLM providers (such as OpenAI and Gemini) and detects abnormal behavior in system usage and performance.  
Anomalies are detected using metrics collected from request logs and monitoring systems.  
When anomalies are identified, alerts or events are generated for monitoring dashboards or alerting systems.

---

# Anomaly Types

## 1. Request Rate Spike

**Description**  
A sudden increase in the number of requests sent to the LLM APIs within a short time period.

**Inputs**
- Number of requests per minute
- Historical request rate baseline

**Detection Approach**
- Compare the current request rate to a baseline average.
- If the request rate exceeds a predefined threshold (for example 3× the normal rate), it is considered an anomaly.

**Output**
- Alert event sent to the monitoring dashboard.
- Metric indicating abnormal traffic spike.

---

## 2. Latency Degradation

**Description**  
A significant increase in response time from the LLM providers.

**Inputs**
- Request latency (response time)
- Historical average latency

**Detection Approach**
- Calculate average latency over a short time window.
- If the latency exceeds a threshold (for example 2× the normal latency), an anomaly is detected.

**Output**
- Alert indicating slow system performance.
- Metric showing increased response time.

---

## 3. Error Rate Spike

**Description**  
A sudden increase in failed LLM requests.

**Inputs**
- Number of failed requests
- Total number of requests
- Error percentage

**Detection Approach**
- Calculate error rate within a time window.
- If the error rate exceeds a defined threshold (for example more than 5% errors), it is flagged as an anomaly.

**Output**
- Alert sent to monitoring or incident management system.
- Error rate metric recorded for dashboards.

---

## 4. Token or Cost Drift

**Description**  
Unexpected increase in token usage or cost per request.

**Inputs**
- Token usage per request
- Cost per request
- Historical average token usage

**Detection Approach**
- Compare token usage with historical averages.
- If token usage or cost per request increases significantly beyond normal limits, it is considered abnormal.

**Output**
- Alert indicating abnormal cost usage.
- Metric showing cost anomaly.

---

# Design Decision

## Real-Time Detection vs Batch Detection

The anomaly detection system is designed to run in **real-time**.

### Reason
Real-time monitoring allows the system to quickly identify issues such as request spikes, latency problems, or cost anomalies.

### Implementation
- Metrics are continuously collected by the monitoring service.
- The anomaly detection service analyzes incoming metrics streams.
- When a threshold or statistical rule is triggered, an alert is immediately generated.

### Benefits
- Faster incident detection
- Reduced operational risk
- Immediate visibility into abnormal system behavior