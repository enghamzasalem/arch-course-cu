# Task 2.1 - Quality Attributes Analysis

## 1. Security

**Definition** 

Security is an external/dynamic quality attribute.  
It ensures that only authorized users can access the system and that data is protected.

**Why It Is Important** 

The system controls sensitive devices such as door locks and security cameras.  
Unauthorized access could create serious safety risks.

**How the Architecture Supports It**  
- Dedicated Authentication Service  
- JWT-based authentication  
- Role-based authorization  
- HTTPS communication between clients and backend  
- Secured MQTT communication between devices and the MQTT Broker 

**Trade-offs**  
- Stronger authentication increases response time  
- Encryption and validation add processing overhead  
- Security increases architectural complexity  

---

## 2. Availability

**Definition** 

Availability is an external/dynamic quality attribute.  
It describes whether the system is accessible and operational when users need it.

**Why It Is Important**

In a Smart Home system, users must be able to control lights, locks, and alarms at any time.  
If the system is down, users lose access to all smart home functions.

**How the Architecture Supports It**  
- Services are separated (Device Manager, Automation, Notification). This separation limits the effect of a failure in one component on the rest of the system.
- Separate operational and telemetry databases reduce overload  
- MQTT Broker ensures reliable message delivery even if some services are temporarily unavailable

**Trade-offs** 
- Redundancy increases infrastructure cost  
- Monitoring and failover mechanisms increase system complexity  

---

## 3. Reliability

**Definition** 

Reliability is an external/dynamic quality attribute.  
It refers to the system's ability to execute operations correctly and consistently without errors.  
Unlike availability, reliability focuses on correct behavior of the system, not just whether it is accessible.

**Why It Is Important**  

Users must trust that when they send a command (e.g., turn on a light), it will execute correctly.  
Frequent failures would reduce user trust.

**How the Architecture Supports It**  
- Device Manager as a single communication hub ensures consistent command handling  
- Clear service separation prevents interference between features  
- MQTT Broker manages device message routing with QoS (Quality of Service) levels  
- Database separation to reduce overload and prevent data corruption  
- Acknowledgment mechanisms confirm command execution

**Trade-offs**  
- Retry mechanisms may increase latency  
- Additional safeguards increase implementation complexity  
- QoS levels add network overhead  

---

## 4. Performance

**Definition**  

Performance is an external/dynamic quality attribute.  
It measures how quickly the system responds to user actions.

**Why It Is Important**  

Users expect immediate feedback when controlling smart devices.  
Delays would negatively affect user experience.

**How the Architecture Supports It**  
- Lightweight MQTT protocol for IoT communication  
- Caching recent device state in memory  
- Separate telemetry database for time-based queries  
- REST APIs optimized for client communication  
- Asynchronous processing for non-critical operations

**Trade-offs**  
- Performance optimization may reduce security checks  
- Caching increases memory usage  
- Optimization may reduce modifiability  
- Asynchronous processing adds complexity  

---

## 5. Scalability

**Definition**  

Scalability is an external/dynamic quality attribute.  
It describes the system's ability to handle an increasing number of connected devices and requests without performance degradation.

**Why It Is Important**  

System must handle increasing number of smart devices and automation events within that environment.
If the system cannot handle this growth, users may experience slow response times, missed automation triggers, or device control failures.
This would directly affect user trust and the overall usability of the system.

**How the Architecture Supports It**  
- MQTT publish/subscribe model allows multiple devices to communicate efficiently  
- Device Manager Service centralizes device communication  
- Separate telemetry database handles increasing sensor data  
- Service-based backend prevents a single component from becoming overloaded  
- Horizontal scaling possible for stateless services

**Trade-offs**  
- Supporting more devices increases infrastructure and hosting cost  
- More device communication increases system complexity  
- Higher scalability requirements may require additional monitoring mechanisms  
- Load balancing adds network overhead  

---

## Quality Attribute Priority Matrix

**Most Critical Attributes**

**1. Security**  
The highest priority. The system controls physical devices (e.g., door locks and cameras), so unauthorized access could create serious safety risks.

**2. Availability**  
Users must be able to access and control their devices at any time. System downtime directly affects usability.

**3. Reliability**  
The system must execute commands correctly and consistently without unexpected failures.

**4. Performance**  
Fast response times are essential for good user experience, but temporary delays are less critical than security or availability failures.

**5. Scalability**  
Important for growth, but can be addressed incrementally as the user base expands.

**Potential Conflicts Between Attributes**

**1. Security vs Performance**  
Strong authentication, encryption, and validation increase processing time and may slightly reduce response speed.

**2. Reliability vs Performance**  
Retry mechanisms and additional safeguards improve reliability but may introduce additional latency.

**3. Availability vs Scalability**  
Supporting both high availability and growing numbers of devices increases infrastructure complexity and cost.

**4. Security vs Availability**  
Overly strict security (e.g., short session timeouts) can reduce availability by forcing frequent re-authentication.

**5. Reliability vs Modifiability**  
Strong reliability requirements make it harder to modify the system without extensive testing.

**Balancing Competing Attributes**

1. **For Security and Performance**: Security is enforced at the main entry points (API Gateway and Authentication Service). This keeps the system secure without adding heavy security logic inside every internal component. Hardware acceleration for encryption helps maintain performance.

2. **For Reliability and Performance**: Retry and validation mechanisms are implemented carefully to improve correctness without significantly degrading responsiveness. Non-critical operations use asynchronous processing.

3. **For Availability and Scalability**: The system is divided into multiple services so that increasing device load does not directly cause full system downtime. Auto-scaling adds capacity during peak loads.

4. **For Security and Availability**: Authentication services are deployed redundantly across multiple zones. Session caching reduces authentication overhead while maintaining security.

5. **For Reliability and Modifiability**: Comprehensive test automation ensures modifications don't introduce reliability issues. Canary deployments gradually roll out changes.

---

## Summary Matrix

| Quality Attribute | Type | Priority | Main Architectural Support |
|:------------------|:-----|:--------:|:---------------------------|
| **Security** | External/Dynamic | 1 | Auth Service, JWT, HTTPS, MQTT security |
| **Availability** | External/Dynamic | 2 | Service separation, database separation |
| **Reliability** | External/Dynamic | 3 | Device Manager hub, MQTT QoS, acknowledgments |
| **Performance** | External/Dynamic | 4 | MQTT protocol, caching, async processing |
| **Scalability** | External/Dynamic | 5 | Publish/subscribe, horizontal scaling |

---

## Grading Checklist

- [x] 5 quality attributes identified
- [x] Each attribute includes definition (internal/external, static/dynamic)
- [x] Clear explanation of importance for smart home system
- [x] Architecture support described for each attribute
- [x] Trade-offs identified for each attribute
- [x] Priority matrix showing most critical attributes
- [x] Conflict analysis between attributes
- [x] Balancing strategies for competing attributes
- [x] Consistent formatting throughout