# Part 3: Architecture Model Documentation

**Video Streaming Platform** — modeling approach, diagram index, and consistency notes.

---

## a) Modeling Approach

### Notations Used

- **C4 Model** (Levels 1–3): System Context, Container, and Component diagrams.
- **UML**: Sequence diagram (user watches video), Deployment diagram (infrastructure).

### Why These Notations

- **C4** gives a clear hierarchy (context → containers → components) and is well-suited for explaining the system to both technical and non-technical stakeholders. Level 1 shows the system boundary and external actors; Level 2 shows main applications and data stores; Level 3 zooms into one container (API Gateway) to show internal components.
- **UML Sequence** is used to describe one critical flow (playback) with participants and message order, including sync request/response and the role of the CDN.
- **UML Deployment** shows where containers run (nodes), which artifacts are deployed, and network relationships (including cloud and edge stereotypes).

### How the Diagrams Relate

- **Context** defines the system (Video Streaming Platform), its users (Subscriber, Content Creator, Admin), and external systems (Payment Gateway, CDN).
- **Container** diagram expands the system into Web App, Mobile App, Smart TV App, API Gateway, Recommendation Service, Streaming Service, Database, and Cache. These are the same conceptual elements that appear in the deployment view.
- **Component** diagram zooms into the API Gateway container and shows Auth, Router, Catalog Proxy, Playback Proxy, User Profile Proxy, and Rate Limiter. Names and responsibilities align with the API’s role in the container diagram.
- **Sequence** diagram uses the same participants (Web App, API Gateway, Streaming Service, CDN) as in the container view, for the “user watches a video” flow.
- **Deployment** diagram maps each container to nodes: client apps on user devices; API Gateway, Recommendation Service, and Streaming Service on the App Server node; Database and Cache on the DB Server node; video delivery on the CDN node.

---

## b) Diagram Index

| Diagram Name              | Type           | Purpose                                                                 | Audience        |
|---------------------------|----------------|-------------------------------------------------------------------------|-----------------|
| System Context (C4 L1)    | C4 Context     | Show system boundary, users, and external systems (Payment, CDN)        | Everyone        |
| Container (C4 L2)         | C4 Container   | Show main applications and data stores and how they communicate        | Dev, DevOps     |
| Component – API Gateway   | C4 Component   | Show internal structure of the API Gateway (components and dependencies)| Developers      |
| Sequence – User Watches   | UML Sequence   | Show message flow for “user watches a video” (playback use case)        | Dev, QA         |
| Deployment                | UML Deployment | Show infrastructure nodes, deployed artifacts, and network links        | DevOps, SRE     |

---

## c) Consistency Check

### Naming and Alignment

- **System name** “Video Streaming Platform” is used consistently in Context and in the titles of all other diagrams.
- **Containers** (Web App, Mobile App, Smart TV App, API Gateway, Recommendation Service, Streaming Service, Database, Cache) use the same names in the Container diagram, Sequence diagram (where applicable), and Deployment diagram (as artifacts on nodes).
- **External systems** (Payment Gateway, CDN) appear in Context and again in Deployment (CDN as a node). Payment is off-stage in the sequence we documented.
- **API Gateway** components (Auth, Router, Catalog Proxy, Playback Proxy, User Profile Proxy, Rate Limiter) are used only in the Component diagram; the Container diagram shows the API Gateway as a single container, and the Sequence diagram shows “API Gateway” as one participant.

### Assumptions and Simplifications

- **Context**: Only three user types (Subscriber, Content Creator, Admin) and two external systems (Payment Gateway, CDN). Other actors (e.g. analytics) or systems (e.g. email) are omitted.
- **Containers**: Smart TV shown as one container; in reality it might be multiple platform-specific apps. Recommendation and Streaming are separate services; no message queue is shown for simplicity.
- **Component**: Only the API Gateway is decomposed; other containers (e.g. Recommendation Service) are not expanded to component level.
- **Sequence**: Single path (happy path) for “user watches a video”; no error or retry flows. CDN is shown as one participant; in reality the client talks to many edge nodes.
- **Deployment**: One region; no multi-region or replication details. CDN is shown as one logical node representing the edge network.

### Cross-Diagram Verification

- Every container in the Container diagram appears in the Deployment diagram (as an artifact on some node or on the client).
- The Sequence diagram’s participants (Web App, API Gateway, Streaming Service, CDN) match containers or external systems from the Container/Context diagrams.
- The Component diagram’s “API Gateway” is the same container as in the Container and Deployment diagrams.

---

## Diagram Files

- **Part 1 (C4):** `part1_context_diagram.drawio`, `part1_container_diagram.drawio`, `part1_component_diagram.drawio`
- **Part 2 (UML):** `part2_sequence_diagram.drawio`, `part2_deployment_diagram.drawio`

PNG exports of the diagrams can be attached to the PR separately (screenshots or images in the PR description).

---
