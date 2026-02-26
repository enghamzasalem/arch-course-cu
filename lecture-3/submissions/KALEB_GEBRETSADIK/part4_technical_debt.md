# Part 4.1: Technical Debt Analysis

## Identified Technical Debt Items

### 1. Unified Relational Database for High-Frequency Telemetry
- **Description**: The current architecture routes high-frequency IoT telemetry (e.g., temperature changes every second) directly into the primary PostgreSQL relational database alongside user accounts and configuration data.
- **Type**: Architectural
- **Severity**: High
- **Principal (Cost to Fix)**: Implementing a dedicated Time-Series Database (TSDB like InfluxDB) and rewriting the data-access layer in the telemetry service. (Estimated effort: 3 sprints).
- **Interest (Ongoing Cost)**: As devices scale, the relational database will experience severe write contention, increasing query latency for UI requests and requiring expensive vertical scaling of the PostgreSQL instance.
- **Impact**: Database lockups, slow dashboard loads for users, and potential data loss if the DB cannot handle the write throughput during peak times.

### 2. Lack of Automated Integration Tests for Message Broker
- **Description**: While unit tests exist for individual services, there is no automated test harness to verify the end-to-end flow of MQTT messages between the Device Manager, Broker, and Security Service.
- **Type**: Test
- **Severity**: Medium
- **Principal (Cost to Fix)**: Developing a test framework using Testcontainers to spin up a local MQTT broker and assert message delivery during the CI pipeline. (Estimated effort: 1 sprint).
- **Interest (Ongoing Cost)**: Manual testing is required for every release to ensure event routing works. Increased risk of regression bugs reaching production.
- **Impact**: Developer slowdown during QA phases and occasional broken routines when message payload structures change without detection.

### 3. Hardcoded External API Integrations in the Security Service
- **Description**: The Security Service currently hardcodes the HTTP calls and authentication logic for third-party notification providers (Twilio for SMS, SendGrid for Email) directly into its business logic.
- **Type**: Code / Dependency
- **Severity**: Low
- **Principal (Cost to Fix)**: Refactoring the service to use an Adapter/Facade pattern for notifications and extracting provider configurations to environment variables or a config server. (Estimated effort: half a sprint).
- **Interest (Ongoing Cost)**: Changing to a cheaper SMS provider requires code changes, a full rebuild, and deployment of the Security Service.
- **Impact**: Vendor lock-in and increased time-to-market when marketing/operations request new notification channels.

---

## Technical Debt Backlog

Below is the prioritized backlog for addressing the identified technical debt.

1. **Unified Relational Database for High-Frequency Telemetry**
   - **Interest Rate**: **High** (Directly degrades user experience and hardware costs scale exponentially).
   - **Impact**: **High** (Threatens overall system availability).
   - **Effort to Fix**: High.
   - **Rationale**: Must be addressed first because it poses an existential threat to the scalability and stability of the entire platform.

2. **Lack of Automated Integration Tests for Message Broker**
   - **Interest Rate**: **Medium** (Developer time wasted on manual QA).
   - **Impact**: **Medium** (Bugs may reach production, but doesn't crash the system under load).
   - **Effort to Fix**: Medium.
   - **Rationale**: Addressed second to stabilize releases and improve developer velocity, ensuring reliable delivery before adding new features.

3. **Hardcoded External API Integrations in the Security Service**
   - **Interest Rate**: **Low** (Only costs money/time when we actively decide to switch vendors).
   - **Impact**: **Low** (Does not affect system performance or current users).
   - **Effort to Fix**: Low.
   - **Rationale**: Placed at the bottom of the backlog. It is an annoyance but doesn't threaten system stability or significantly drain daily developer resources. We will fix this when the business requests a new notification provider.
