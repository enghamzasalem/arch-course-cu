#  Architectural Smells Detection


# 1. Identified Architectural Smells

## Smell 1: God Component

**Where it Appears:**  
The Device Manager Service sometimes handles too many responsibilities, such as device state, scheduling, and direct communication with multiple external services.

**Why it’s a Problem:**  
- Violates the single responsibility principle  
- Hard to test and maintain  
- Changes in one area can affect unrelated functionality

**Proposed Solution:**  
- Split Device Manager into smaller services or internal modules:  
  - Device State Service  
  - Device Scheduler Service  
  - Device Communication Service  
- Use the **Mediator Pattern** or internal event system for coordination between modules


## Smell 2: Cyclic Dependency (Circular Events)

**Where it Appears:**  
In the message broker logic, Service A publishes an event that Service B consumes; Service B then publishes an event that Service A consumes to finish a task.

**Why it’s a Problem:**  
- Deadlocks: This creates a circular dependency at the architectural level that is extremely hard to debug.
- Infinite Loops: A small bug in event logic can cause services to trigger each other indefinitely, crashing the Message Broker.  


**Proposed Solution:**  
- Directed Acyclic Graphs (DAG): Ensure the event flow always moves in one direction. 
- Orchestration: Use a central "Saga Orchestrator" to manage complex cross-service flows instead of letting services trigger each other in circles. 

# 2. Refactoring Diagram Explanation

**Before Refactoring:**  
- Logic Bloat: Device Manager is monolithic and difficult to modify without side effects.
- Circular Risks: Services are potentially triggering each other in loops through the broker. 


**After Refactoring:**  
- Modularization: Device Manager is split into focused components (State, Scheduler, Comm).
- Complex transactions are managed by a state machine to prevent circular event smells.

