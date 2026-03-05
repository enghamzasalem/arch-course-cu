# Part 3 - Architecture Documentation
# Task 3.1 - Model Documentation (Video Streaming Platform)

## a) Modeling Approach

### Notations Used
- **C4 Model**
  - **Level 1 (System Context):** shows the platform boundary, people, and external systems.
  - **Level 2 (Container):** shows the major runtime/deployable building blocks (apps, API, DB, storage) and how they communicate.
  - **Level 3 (Component):** decomposes one container (in this submission: the API Gateway) into internal components and their dependencies.
- **UML**
  - **Sequence Diagram:** shows time-ordered interactions for the use case "User watches a video".
  - **Deployment Diagram:** shows infrastructure nodes, deployed artifacts, and network connections.

### Why These Notations
- They were expected to be used in this assignment.

- C4 was chosen because it gives a clean, hierarchical "zooming-in" path:
  Context --> Containers --> Components, which makes it easy to communicate with different audiences.
  
- UML was used where behavior and infrastructure matter:
  - **Sequence** captures runtime interactions and API calls in a single use case flow.
  - **Deployment** makes the physical runtime environment explicit (nodes, artifacts, and protocols). 

### How the Diagrams Relate

The diagrams describe the system from different perspectives and levels of detail.

- **C4 Level 1 (Context)** shows the platform at a high level, including users and external systems.  
- **C4 Level 2 (Container)** breaks the platform into its main containers such as the Web App, API Gateway, Services, and Databases.  
- **C4 Level 3 (Component)** focuses on the internal components of the API Gateway container.
- **Sequence Diagram** shows how these parts interact when a user watches a video.
- **Deployment Diagram** shows how the system is deployed on the infrastructure.

Overall, the **C4 diagrams** describe the structure of the system at different levels, while the **UML diagrams** show system behavior and deployment.

---

## b) Diagram Index

**System Context Diagram (C4 Level 1)**  
Type: C4 Model  
Purpose: Shows the overall system boundary, the users interacting with the platform, and external systems such as the CDN and payment gateway.  
Audience: Stakeholders and developers.
Reference: ![System Context Diagram (C4 L1)](part1_context_diagram.png)

**Container Diagram (C4 Level 2)**  
Type: C4 Model  
Purpose: Shows the main containers of the platform such as the Web App, Mobile App, API Gateway, Services, and Databases, and how they communicate with each other.  
Audience: Developers and system architects.
Reference: ![Container Diagram (C4 L2)](part1_container_diagram.png)

**Component Diagram - API Gateway (C4 Level 3)**  
Type: C4 Model  
Purpose: Shows the internal components of the API Gateway container, including the Request Router, Authentication Middleware, Rate Limiter, and Service Discovery Client.  
Audience: Developers.
Reference: ![Component Diagram (C4 L3)](part1_component_diagram.png)

**Sequence Diagram - User Watches Video**  
Type: UML Sequence Diagram  
Purpose: Shows the interaction flow when a user clicks on a video, the system validates authentication, generates a signed URL, and streams content from the CDN.  
Audience: Developers and testers.
Reference: ![Sequence Diagram](part2_sequence_diagram.png)

**Deployment Diagram**  
Type: UML Deployment Diagram  
Purpose: Shows the infrastructure setup of the platform including cloud providers, availability zones, servers, and network connections between them.  
Audience: Developers and DevOps engineers.
Reference: ![Deployment Diagram](part2_deployment_diagram.png)

---

## c) Consistency Check

### How Consistency Was Ensured

Consistency between the diagrams was maintained mainly by using the same names for the main system elements. 
For example, components such as API Gateway, User Service, Streaming Service, CDN, and Object Storage appear across multiple diagrams and represent the same parts of the system.

The protocols used between components are also consistent. The Web App communicates with the API Gateway using HTTPS/REST. The API Gateway connects to Services using gRPC and communicates with the CDN using HTTPS. The Streaming Service connects to Object Storage using HTTPS (S3 API).

Responsibilities are also aligned between the diagrams. The API Gateway handles routing and authentication, which is shown in the component diagram. The Streaming Service generates signed URLs, which is reflected in the sequence diagram. The CDN and Object Storage are responsible for video storage and delivery, which is shown in the container, sequence, and deployment diagrams.

Actors remain consistent across diagrams. The Subscriber appears in both the context diagram and the sequence diagram as the user initiating the watch video flow.

---

### Assumptions and Simplifications

Authentication details are not modeled in detail. The sequence diagram shows a simple token validation step rather than the full OAuth flow.

Video streaming is represented in a simplified way. Instead of modeling adaptive bitrate streaming or DASH/HLS protocols, the system simply retrieves a stream URL from the CDN.

The component diagram shows only the API Gateway container. Other containers (User Service, Streaming Service) would have their own internal component diagrams in a complete model.

Video files are stored in Object Storage, which represents a cloud storage service such as AWS S3.

The deployment diagram shows two availability zones within a single region. A production system might have multiple regions for disaster recovery.

Database replication is simplified to primary-replica; real systems might have more complex topologies with read replicas, sharding, and failover configurations.

---

## Diagrams

### 1) System Context Diagram (C4 Level 1)
![System Context Diagram (C4 L1)](part1_context_diagram.png)

### 2) Container Diagram (C4 Level 2)
![Container Diagram (C4 L2)](part1_container_diagram.png)

### 3) Component Diagram - API Gateway (C4 Level 3)
![Component Diagram (C4 L3)](part1_component_diagram.png)

### 4) Sequence Diagram - User Watches Video
![Sequence Diagram](part2_sequence_diagram.png)

### 5) Deployment Diagram
![Deployment Diagram](part2_deployment_diagram.png)