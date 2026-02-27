# Smart Home Management System
## Architecture vs. Design Decisions

**Student Name:** Amaan Shaikh
**Date:** 27th Feb, 2026
**Course:** Software Architecture - Chapter 3

# Task 1.2 - Architecture vs Design Decisions

# Architectural Decisions

## **Decision-1**: Using an API Gateway as the main entry point

All client applications (Mobile App, Web Interface, Voice Assistant) communicate with the backend through an API Gateway.

**Rationale:**  
This makes the system easier to manage because there is only one entry point. The gateway can handle routing, rate limiting, and basic request validation.

**Alternatives Considered:**  
Clients directly calling each backend service.

**Consequences**

**Positive:**
- Easier to control traffic and manage APIs  
- Internal services are hidden from clients

**Negative:**
- The gateway becomes an important component that must be reliable  

---

## **Decision-2**: Using a separate Authentication Service
 
Authentication is handled by a dedicated Authentication Service using JWT tokens.

**Rationale:**  
Keeping authentication separate makes the system more organized and avoids repeating authentication logic in each service.

**Alternatives Considered:**  
Handling authentication inside the API Gateway or inside each individual service.

**Consequences**

**Positive:**  
- Centralized security management  
- Cleaner separation of responsibilities

**Negative:**  
- Adds an extra service to maintain  

---

## **Decision-3**: Splitting the backend into multiple services
  
The backend is divided into Device Manager Service, Automation Service, and Notification Service.

**Rationale:**  
Each service has a clear responsibility. This improves modularity and makes the system easier to understand and maintain.

**Alternatives Considered:**
Using a single larger service that handles all functionalities.

**Consequences** 

**Positive:**
- Better separation of concerns  
- Easier to update one feature without affecting everything  

**Negative:**
- Services need to communicate with each other  

---

## **Decision-4**: Use the Device Manager Service as the single communication hub for devices

All smart devices communicate only with the Device Manager Service. Other services do not talk to devices directly.

**Rationale:**  
This keeps device-specific logic in one place and avoids duplicated integration code across services. It also makes the system easier to maintain and extend when new device types are added.

**Alternatives Considered:**  
Allowing each service (e.g., Automation or Notification) to communicate directly with devices.

**Consequences**  

**Positive:**
- Clear separation of responsibilities and simpler device integration  
- Easier to troubleshoot device-related issues 

**Negative:**
- Device Manager becomes a critical component and must be reliable 

---

## **Decision-5**: Using separate databases for operational and telemetry data
 
The system uses two databases:  
- Operational Database: For users, devices, and routines  
- Telemetry Database: For energy consumption and sensor data  

**Rationale:**  
Operational data and telemetry data have different usage patterns. Separating them improves performance and organization.

**Alternatives Considered:**  
Using a single database for all types of data.

**Consequences**  

**Positive:**
- Better data organization  
- Improved performance for time-based data  

**Negative:**
- Slightly more complex data management  

---

# Design Decisions

## **Decision-1**: Using an interface-based structure for device handling
 
Device-specific logic is implemented behind a common interface in the Device Manager Service.

**Rationale:**  
This makes it easier to support different types of smart devices.

**Design Pattern:**  
Strategy Pattern

**Scope:**  
Inside the Device Manager Service.

---

## **Decision-2**: Caching recent device state
 
Recent device states are stored temporarily in memory.

**Rationale:**  
This improves performance when users frequently check device status.

**Scope:**  
Device Manager Service.

---

## **Decision-3**: Splitting validation responsibilities
 
Basic request validation is done at the API Gateway, while business logic validation is handled inside each service.

**Rationale:**  
This keeps the system more organized and secure.

**Scope:**  
API Gateway and backend services.

---

## **Decision-4**: Using a relational schema for operational data
 
Operational data such as users, devices, and routines are stored in a relational database.

**Rationale:**  
These entities have clear relationships and structured queries are useful.

**Design Pattern:**  
Repository Pattern

**Scope:**  
Operational Database.

---

## **Decision-5**: Storing alert history in the operational database

Alert metadata is stored in the Operational Database.

**Rationale:**  
This allows users to review previous alerts and system activity.

**Scope:**  
Notification Service and Operational Database.