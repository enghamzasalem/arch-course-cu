# Component Rationale – Proxy Gateway Container

## Overview
The Proxy Gateway container acts as the entry point for all LLM requests.
To achieve modularity and separation of concerns, it is decomposed into
four components, each with a clear responsibility.

---

## 1. RequestValidator
**Responsibility:**
Validates incoming requests from client applications.

**Why separate component:**
Validation logic may evolve independently from routing or response handling.
Separating it improves maintainability and testing.

**Provided Interface:**
Validated request for downstream processing.

---

## 2. ProviderRouter
**Responsibility:**
Determines which LLM provider should handle the request (OpenAI or Gemini).

**Why separate component:**
Routing logic may depend on configuration, load balancing, or cost policies.
Encapsulation allows easy addition of new providers.

**Required Interfaces:**
OpenAI API, Gemini API.

---

## 3. ResponseNormalizer
**Responsibility:**
Transforms responses from different providers into a unified format.

**Why separate component:**
Different providers return responses with different schemas.
Normalization ensures consistent responses for client applications.

---

## 4. TrackingEmitter
**Responsibility:**
Emits request metadata such as token usage, latency, and cost.

**Why separate component:**
Tracking is independent from request processing and can evolve separately.
It allows asynchronous logging and integration with monitoring systems.

---

## Modularity Principles Applied

### Single Responsibility
Each component has one clear responsibility.

### Low Coupling
Components interact through defined interfaces.

### High Cohesion
All logic inside a component is closely related to its function.

### Extensibility
New providers or tracking mechanisms can be added without modifying core components.