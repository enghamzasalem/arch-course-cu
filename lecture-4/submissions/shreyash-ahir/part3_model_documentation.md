**Architecture Documentation**

**Task 3.1: Model Documentation**

1.  **Modelling Approach**
2.  **Notations which are used in this assignment:**

- In this assignment I used both the modelling Notation C4 and UML. Because this type of application not relay on any particular type of modelling approach.

1.  **Reason behind for choosing this :**

- **C4:** Video streaming sites like Netflix demand specific architectural views for developers, product managers, and other relevant parties. C4 Model provides these architectural views on four different hierarchical levels: Context, Containers, Components, and Code. It provides an appropriate level of abstraction without the complexity of using the Unified Modelling Language. Box and arrow diagrams make it easy to understand and maintain system architectures for both technical and non-technical people.
- **UML:** For detailed internal design, it has been found that UML diagrams such as Class Diagrams and Sequence Diagrams can come in handy. These can assist the developers in understanding the complex aspects of the system, such as the relationship of classes to one another, as well as the sequence of events in the system, such as in the video upload process. The role of UML is primarily to perform detailed modelling of classes, object interactions, states, and behaviour when detailed technical documentation is necessary.

1.  **Points where both diagram can rely on each other:**

- C4 Model and UML diagrams can be used together by showing the system from different angles. The C4 Model can be used to show the "big picture" of the system, including the system context, then the containers, then the components, so that everyone can see how the major pieces of the system fit together.
- After the "big picture" of how the system fits together, UML diagrams can be used to show the nitty-gritty of how the individual pieces of the system operate. For example, a UML Class Diagram can be used to show how classes relate to one another, while a UML Sequence Diagram can be used to show how interactions occur.

1.  **Diagram Index**

|     |     |     |     |
| --- | --- | --- | --- |
| **Name** | **Type** | **Purpose** | **Audience** |
| System Context | C4 Level-1 | Demonstrates how Video Streaming Platform interacts with users (Subscriber, Creator, and Admin) and external systems (CDN, Payment Gateway). | Technical & Non-technical stakeholders |
| Container | C4 Level-2 | Divides Video Streaming Platform into high-level components such as Web/Mobile Apps, API Gateway, and Micro services/Databases. | Developers & Product Managers |
| Component | C4 Level-3 | Takes a deeper look into Streaming & Metadata API and its internal components such as Auth Controller, Search Engine, and Catalog Manager. | Developers & Architects |
| Sequence | UML (Behavioural) | Represents dynamic and conditional logic for a Secure Video Playback Initiation process. | Developers |
| Deployment | UML (Structural) | Links software components such as Docker Containers to physical components such as Application Servers and Load Balancers. | Infrastructure & DevOps Engineers |

1.  **Consistency Check**
2.  **Points to maintain the consistency across diagrams:**

- **Standard Naming Conversion:** Naming conventions across all levels. The Streaming & Metadata API in Level 2 is still the parent boundary for all Level 3 components, such as the Streaming Manager.
- **Unified Actor Roles:** The roles of Subscriber, Content Creator, and Admin are consistent from the System Context to the Sequence Diagram.
- **Interface Continuity:** External interfaces, such as the CDN and Payment Gateway, use the same grey box notation and naming conventions in all diagrams.
- **Cross-Level Traceability:** The API Gateway is the entry point for the "Secure Video Playback" sequence and is a Docker artifact in the deployment view.

1.  **Assumption and Simplifications:**

- **Internal Service:** C4 level 2 assumes that micro services (e.g., Recommendation Service) behave as single components and hide their internal load balancing and data stores
- **Sequential Logic:** Sequence Diagram shows the Happy Path and primary Unauthorized error for playback but does not include finer error states such as CDN timeouts or DB connection issues
- **Deployment:** Deployment Diagram shows a simplified cloud environment (e.g., one Database Server and Load Balancer) to represent the deployment architecture without replication and auto-scaling details
- **Statelessness:** API Gateway verifies sessions using JWTs/tokens and thus keeps the system stateless for scaling across Application Servers.

1.  **Reference:**

- Gemini Ai
- C4model.com
- Perplexity