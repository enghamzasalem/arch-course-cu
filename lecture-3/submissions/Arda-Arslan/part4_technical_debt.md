# Part 4.1 - Technical Debt Analysis

## Technical Debt Item 1 - API Gateway as a Single Point of Failure

**Description**  

The API Gateway is the only public entry point of the system.  
All client applications communicate through it.  
If the gateway runs as a single instance and it fails, the whole system becomes inaccessible.

**Type**  

Architectural

**Severity** 

High

**Principal (Cost to Fix)**  

- Deploy more than one API Gateway instance  
- Add a Load Balancer  
- Configure basic health checks and monitoring  

**Interest (Ongoing Cost)**  

- If the gateway crashes, users cannot access any service  
- System downtime affects user experience  
- Emergency fixes may be needed during failures  

**Impact**  

-If the API Gateway fails, users cannot log in, control devices, or receive updates. The entire system becomes unusable.

---

## Technical Debt Item 2 - Device Manager as a Centralized System Bottleneck

**Description**  

All smart devices communicate only with the Device Manager Service through the MQTT Broker.  
While this simplifies the design, it may cause overload if the number of devices increases significantly.

**Type**  

Architectural

**Severity**

High

**Principal (Cost to Fix)**  

- Allow multiple Device Manager instances  
- Improve message handling and performance testing  
- Separate some responsibilities if needed (e.g., commands and telemetry)

**Interest (Ongoing Cost)**  

- Slower response times when many devices are connected  
- Possible delays in automation routines  
- Reduced system performance under high load  

**Impact**  

-Users may experience delayed device responses or failed commands. Automation routines may not execute at the expected time during high load.

---

## Technical Debt Item 3 - Limited Monitoring and Logging

**Description**  

The system contains multiple services and asynchronous communication (MQTT).  
If there is no centralized logging or monitoring, it becomes difficult to detect and debug problems across services.

**Type**  

Operational / Architectural

**Severity** 

Medium

**Principal (Cost to Fix)**  

- Add centralized logging  
- Monitor service health and error rates  
- Track basic performance metrics  

**Interest (Ongoing Cost)**  

- Longer time to detect and fix errors  
- Harder troubleshooting of distributed issues  
- Increased maintenance effort  

**Impact**  

-System issues may take longer to detect and resolve. Small problems may grow into larger failures before being noticed.

---

# Technical Debt Backlog (Prioritized)

## Priority 1 - API Gateway as a Single Point of Failure

- **Interest rate:** High - If the gateway fails, the entire system becomes inaccessible.  
- **Impact on system:** Very high - Users cannot log in, control devices, or receive updates.  
- **Effort to fix:** Medium - Requires replication, load balancing, and monitoring configuration.

This item is the highest priority because it directly affects the whole system and creates immediate downtime risk.

## Priority 2 - Device Manager as a Centralized System Bottleneck

- **Interest rate:** High - Performance problems increase as the number of connected devices grows.  
- **Impact on system:** High - Users may experience delayed commands or failed automation routines.  
- **Effort to fix:** High - Requires scaling strategy and possible architectural adjustments.

This item is second because it strongly affects system behavior under load, but it does not immediately stop the entire system like the gateway failure would.

## Priority 3 - Limited Monitoring and Logging

- **Interest rate:** Medium - Problems may go unnoticed for longer periods.  
- **Impact on system:** Medium - Issues are harder to detect and resolve, but the system can still operate.  
- **Effort to fix:** Medium - Adding logging and monitoring tools is manageable compared to architectural refactoring.

This item is third because it does not directly stop functionality, but it increases operational risk over time.

