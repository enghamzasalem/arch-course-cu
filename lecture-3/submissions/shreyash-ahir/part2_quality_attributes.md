**Part 2 – Quality Attributes**

**Quality Attributes for Smart Home System**

**(2.1)**

**Performance**

Performance is an external and dynamic quality attribute that measures system responsiveness and latency. It is important because users expect instant control of devices and real-time security alerts. The architecture supports performance through microservices for independent scaling, MQTT for lightweight IoT communication, caching to reduce database calls, and event-driven messaging for asynchronous processing. The trade-off is increased infrastructure cost and possible temporary data inconsistency due to caching.

**Security**

Security is an external quality attribute with both static and dynamic aspects, ensuring protection against unauthorized access and data breaches. It is critical because the system controls door locks, cameras, and sensitive user data. The architecture supports security using an API Gateway with JWT authentication, HTTPS communication, role-based access control, and encrypted storage. The trade-off is slightly higher latency and reduced usability due to strict authentication mechanisms.

**Scalability**

Scalability is an external and dynamic attribute that enables the system to handle increasing users and devices. It is important because smart homes continuously add more IoT devices. The system supports scalability using microservices, cloud deployment with elastic scaling, and message queues for load distribution. The trade-off is higher system complexity and operational cost.

**Reliability / Availability**

Reliability and availability are external and dynamic attributes that ensure continuous and correct system operation. They are crucial because security systems and smart locks must function 24/7. The architecture ensures reliability through cloud redundancy, service isolation, and reliable messaging. The trade-off is increased infrastructure cost and monitoring complexity.

**Maintainability**

Maintainability is an internal and static attribute that refers to ease of modification and extension. It is important due to frequent updates, new device integrations, and feature enhancements. The architecture supports maintainability through microservices separation, repository pattern usage, and clear API contracts. The trade-off is higher deployment and DevOps complexity.

**Quality Attribute Priority Matrix**

| **Priority** | **Quality Attribute** |
| --- | --- |
| 1   | Security |
| 2   | Reliability / Availability |
| 3   | Performance |
| 4   | Scalability |
| 5   | Maintainability |

Security and Reliability are highest because system controls physical home access.

&nbsp;**Attribute Conflicts:**

| **Attribute A** | **Conflicts With** | **Reason** |
| --- | --- | --- |
| Security | Performance | Encryption & authentication increase latency |
| Scalability | Maintainability | Distributed systems are harder to manage |
| Performance | Reliability | Redundancy may reduce speed |
| Maintainability | Performance | Abstraction layers may reduce efficiency |

**How Competing Attributes Were Balanced**

1.  Security prioritized over Performance.  
    Used HTTPS + JWT even if slight latency increase.
2.  Reliability balanced with Cost.  
    Cloud redundancy but selective scaling.
3.  Scalability balanced with Maintainability.  
    Microservices with API Gateway to reduce coupling.
4.  Performance balanced using Caching + Async Messaging.  
    Reduced synchronous bottlenecks**.**