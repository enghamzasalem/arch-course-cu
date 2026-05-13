# Part 4.2 - Architectural Smells Detection

## Smell 1 - God Component (Device Manager)

**Where It Appears**

The Device Manager Service is responsible for:
- Handling communication with all smart devices  
- Processing MQTT messages  
- Managing device state  
- Sending commands to devices
- Communicates with other services  

**Why It Is a Problem**

This concentrates multiple responsibilities in a single service.
When one component handles too many responsibilities:
- It becomes harder to maintain  
- Changes increase the risk of breaking other functionality  
- Scaling the system becomes more complex  
- Over time, this service may grow too large and difficult to manage.

**Proposed Solution**

Refactor the Device Manager by separating responsibilities, for example:
- Device Communication Module  
- Device State Management Module  
- Command Processing Module  

---

## Smell 2 - Single Point of Failure (API Gateway)

**Where It Appears**

The API Gateway is the only public entry point of the system.  
All client requests depend on it.

**Why It Is a Problem**

If the API Gateway fails:
- The entire system becomes inaccessible  
- Users cannot log in or control devices  
- All services behind it become unreachable  

**Proposed Solution**

Introduce redundancy:
- Deploy multiple API Gateway instances  
- Add a Load Balancer  
- Configure basic failover and monitoring  
