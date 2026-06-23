# Part 2.1 – Component Rationale: Proxy Gateway

![LLM Wrapper Component Diagram](part1_component_diagram.drawio.png)

The **Proxy Gateway container** is responsible for handling the full lifecycle of LLM API requests between internal applications and external providers. To maintain high performance, extensibility, and observability, the gateway is decomposed into four modular components.

This decomposition follows the principles of **separation of concerns** and **single responsibility**, ensuring that each component performs a well-defined task. The modular design also improves maintainability and allows individual components to evolve independently.

---

# Components

## 1. RequestValidator

**Responsibility**

The `RequestValidator` component performs validation on all incoming requests before they are processed further. It enforces the **fail-fast principle** by verifying that requests meet the required criteria.

Key validations include:

* API key verification using a local cache
* Request schema validation
* Input format checks
* Rate limiting or basic security validation

**Rationale**

Placing validation at the very beginning of the request pipeline prevents invalid or unauthorized requests from consuming system resources. It also avoids unnecessary calls to external LLM providers, which could incur additional costs.

By rejecting invalid requests early, the system improves both **efficiency** and **security**.

---

## 2. ProviderRouter

**Responsibility**

The `ProviderRouter` determines which upstream LLM provider should handle the request. Based on configuration or request parameters, it routes requests to providers such as OpenAI or Gemini.

This component also manages provider-specific requirements, including:

* API endpoints
* Authentication headers
* Request formatting

**Rationale**

Centralizing routing logic in a single component simplifies provider integration and improves flexibility. New providers can be added without changing client applications.

Additionally, the router enables advanced features such as:

* **Provider failover** (routing traffic to another provider during outages)
* **Load distribution across providers**
* **Provider-specific optimization strategies**

This abstraction shields client applications from provider-specific differences.

---

## 3. ResponseNormalizer

**Responsibility**

Different LLM providers return responses in different formats. The `ResponseNormalizer` converts these provider-specific responses into a **common internal schema** used throughout the system.

The normalized format includes fields such as:

* Generated text
* Token usage
* Request latency
* Model name
* Estimated cost

**Rationale**

Normalizing responses ensures that downstream components do not need to understand provider-specific formats. This significantly simplifies the design of other services such as telemetry ingestion and anomaly detection.

By introducing a consistent internal representation, the system improves **maintainability, interoperability, and extensibility**.

---

## 4. AsyncTelemetryEmitter

**Responsibility**

The `AsyncTelemetryEmitter` produces telemetry events that describe each LLM request. These events include metadata such as request latency, token counts, provider information, and response status.

The component sends this data asynchronously to the **Event Bus**, where it can be processed by downstream monitoring and analytics services.

**Rationale**

This component plays a critical role in supporting the **latency and observability quality attributes**.

Because telemetry emission is **asynchronous and non-blocking**, the user receives their LLM response without waiting for telemetry data to be written to storage. Even if the monitoring pipeline is under heavy load, request handling remains fast and responsive.

This design ensures that observability features do not negatively impact the primary functionality of the system.

---

# Summary

The Proxy Gateway container is decomposed into four components that each address a specific responsibility within the request lifecycle:

| Component             | Responsibility                                            |
| --------------------- | --------------------------------------------------------- |
| RequestValidator      | Validates requests and enforces security rules            |
| ProviderRouter        | Routes requests to the correct LLM provider               |
| ResponseNormalizer    | Converts provider responses into a common internal format |
| AsyncTelemetryEmitter | Emits asynchronous telemetry events for monitoring        |

This modular structure improves system **performance, scalability, and maintainability** while enabling robust monitoring and anomaly detection capabilities.
