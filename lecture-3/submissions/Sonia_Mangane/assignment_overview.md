# Architectural Assumptions 

### A. Smart Home Domain Context
I assumed the system is a Smart Home platform where users manage connected devices (e.g., lights, alarms, sensors), configure automation rules, monitor security events, and track energy usage. All architectural decisions were designed to support these core capabilities.

### B. Scalability Requirements
I assumed the system must support a growing number of users and connected devices over time. To address this, we adopted a Microservices architecture and Cloud-based deployment to enable horizontal scaling and future expansion.

### C. High Availability and Fault Isolation
I assumed the system must remain operational even if individual components fail, particularly for critical features such as security alerts. This requirement influenced the adoption of Microservices, Event-Driven Architecture, and the Database-per-Service pattern to isolate failures and improve resilience.

### D. Service Independence and Team Autonomy
I assumed services should be independently developed, deployed, and maintained, potentially by separate teams. To minimize coupling and direct dependencies between services, we introduced a Message Broker, API Gateway, and enforced Database-per-Service isolation.

### E. Acceptance of Eventual Consistency
I assumed that strict real-time consistency across services is not required and that short synchronization delays are acceptable. This allowed us to adopt asynchronous, event-driven communication, improving scalability and decoupling at the cost of immediate consistency.

## 1. Architeture design and Design Patterns

### 1.1 System Goals:
I started by defining what the Smart Home system actually needs to do. I identified the core users (Homeowners) and the big-picture goals, like making sure the house is secure and energy-efficient. This later helped me identify which functional and non-fuctional requirements to prioritize.


### 1.2 Architecture vs. Design: 
I had to learn the difference between architecture design, which focuses on how componets communicate externally and design patterns which help frame the inner workings of the component. I decided on a hybrid architecture - Microservices + Event-Driven architecture. 

## 2. Quality Attributes & Views 

### 2.1 Quality Attributes: 
I realized a smart home is useless if it’s slow or crashes. I prioritized Availability (the lights must always turn on) and Scalability (the system shouldn't break if I add 50 new sensors).

### 2.2 Multiple Views: 
I looked at the system from different angles. I created a Logical View to show how the code is organized and a Sequence View to show a use case that helps demonstrate how the components interact with each other. I have also included a physical view which shows where each component is to be deployed.

## 3. Architectural Pattern

This was the most difficult choice. I went with a Hybrid Microservices + Event-Driven approach.

- I used Microservices so that if the "Weather Service" goes down, the "Security Service" still works.
- I used an Event-Bus so services can "talk" to each other without being stuck waiting for a response.
- I followed the Database-per-Service rule to make sure no two services were fighting over the same data.

## 4. Debt & Refactoring 

### 4.1 Technical Debt: 
I took an honest look at my design and found "Debt"—short-cuts I took that would hurt us later. I identified a God Component (one service doing too much) and a Cyclic Dependency (services talking in circles).

### 4.2 Refactoring: 

- I split the God Component into smaller, focused pieces (State, Scheduler, Comm).
- I fixed the Circular Loops by introducing a Saga Orchestrator to act as a "traffic cop," ensuring events move in a straight line instead of a loop.

Overall, I moved the system from a 'monolithic' way of thinking into a truly distributed one. It's more complex now, but it's built to grow without falling apart.
