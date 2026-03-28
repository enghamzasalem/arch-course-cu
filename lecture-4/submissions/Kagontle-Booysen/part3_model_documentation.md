# 🎬 Video Streaming Platform — Architecture Diagrams

A complete set of architecture diagrams for a Netflix-style video streaming platform, covering C4 Model (Levels 1–3) and UML diagrams (Sequence + Deployment).

---

## 📁 File Index

| File | Type | Description |
|------|------|-------------|
| ` part1_context_diagram.png` | C4 Level 1 | System boundary, actors, and external systems |
| `part1_container_diagram.drawio` | C4 Level 2 | All 15 containers with technology labels and protocols |
| 'part1_component_diagram.drawio` | C4 Level 3 | Recommendation Engine decomposed into 6 components |
|  'part2_sequence_diagram.drawio` | UML Sequence | "User Watches a Video" message flow |
| ` part2_deployment_diagram.drawio` | UML Deployment | AWS infrastructure nodes and artifact mapping |
| `part3_model_documentation.html` | Documentation | Full modeling report with all diagrams embedded |
| `part3_model_documentation.md` | Documentation | Markdown version of the modeling report |
| `part3_model_documentation.docx` | Documentation | Word version of the modeling report |

---

## 🚀 How to View

Place all files in the **same folder**, then open `part3_model_documentation.html` in your browser.

```
video-streaming-diagrams/
├── part1_context_diagram.png
├── part1_container_diagram.png
├── part1_component_diagram.png
├── part2_sequence_diagram.png
├── part2_deployment_diagram.png
└── part3_model_documentation.md   ← start here
```



---

## a) Modeling Approach

### Modeling Notations Used

Two complementary modeling notations were used for this architecture documentation:

1. **C4 Model** (Context, Containers, Components, Code)
   - Used for Part 1 diagrams to show progressive levels of detail
   - Chosen because it provides hierarchical views suitable for different stakeholders
   - Excellent for showing how containers from Part 1 map to deployment nodes in Part 2

2. **UML Deployment Diagrams** (Unified Modeling Language)
   - Used for Part 2 infrastructure diagram
   - Chosen because UML Deployment diagrams are specifically designed to show:
     - Physical hardware nodes
     - Software artifacts deployed on nodes
     - Network connections between nodes
     - Runtime environments and dependencies

### Why These Notations Were Chosen

| Notation | Strengths | Why Appropriate |
|----------|-----------|-----------------|
| **C4 Model** | Progressive disclosure of detail · Stakeholder-specific views · Container focus for microservices | Perfect for showing application architecture from high-level to code-level, matching our container-based design |
| **UML Deployment** | Hardware/software mapping · Network topology · Physical infrastructure focus | Ideal for showing where containers run and how they connect physically |

### How the Diagrams Relate to Each Other

```
C4 Context Diagram (Level 1)
        ↓
C4 Container Diagram (Level 2) ◄─────────────┐
        ↓                                     │
C4 Component Diagram (Level 3)           Maps to
        ↓                                     │
UML Deployment Diagram ───────────────────────┘
(Physical Infrastructure)
```

**Relationship Mapping:**
```
├── C4 Container "Web App"       → Runs on Web Server Node
├── C4 Container "API"           → Runs on Application Server Node
├── C4 Container "Database"      → Runs on Database Server Node
└── C4 Container "Static Assets" → Distributed via CDN Node
```

---

## b) Diagram Index

| Diagram Name | Type / Notation | Purpose | Audience |
|---|---|---|---|
| **System Context** | C4 Level 1 | Show system boundaries and external users | Business stakeholders, project managers |
| **Container Diagram** | C4 Level 2 | Show high-level technology choices and responsibilities | Developers, architects, DevOps |
| **Component Diagram** | C4 Level 3 | Show internal components of Recommendation Engine | Development team |
| **Sequence Diagram** | UML Behavioral | Show runtime message flow for "User Watches a Video" | Developers, QA, API designers |
| **Deployment Diagram** | UML Deployment | Show physical infrastructure and node mapping | Operations, DevOps, infrastructure team |

### Diagram Files Reference

```
part1_context_diagram    →  c4-system-context.html
part1_container_diagram  →  c4-container-diagram.html
part1_component_diagram  →  c4-component-diagram-v2.html
part2_sequence_diagram   →  uml-sequence-simple.html
part2_deployment_diagram →  uml-deployment-simple.html
```

### Diagram Previews

#### C4 Level 1 — System Context
![C4 System Context](part1_context_diagram.png)

#### C4 Level 2 — Container Diagram
![C4 Container Diagram](part1_container_diagram.png)

#### C4 Level 3 — Component Diagram
![C4 Component Diagram](part1_component_diagram.png)

#### UML Sequence Diagram
![UML Sequence Diagram](part2_sequence_diagram.png)

#### UML Deployment Diagram
![UML Deployment Diagram](part2_deployment_diagram.png)

---

## c) Consistency Check

### Consistency Measures Implemented

| Element | Consistent Across Diagrams | Verification Method |
|---------|---------------------------|---------------------|
| **System Name** | "Video Streaming Platform" | Same name in all diagrams |
| **External Users** | Subscriber, Content Creator, Admin | Identical actor names |
| **Containers** | C-01 to C-15 with consistent IDs | Same container names in C4 and Deployment |
| **Technology Stack** | React, Go, Node.js, PostgreSQL, Redis, Kafka | Consistent tech labels |
| **Relationships** | HTTPS, REST, gRPC, SQL, RESP, S3 API | Same protocol names on all arrows |

### Assumptions Made

**1. Network Infrastructure**
- Internal network is assumed secure and isolated
- Load balancers exist but are not shown for simplicity
- Firewalls are in place between tiers

**2. Scalability Assumptions**
- Each node can be horizontally scaled
- CDN handles global distribution automatically
- Database replication is handled separately

**3. Simplifications**
- Single database server shown (actual is Multi-AZ with read replicas)
- Load balancers omitted for clarity
- Monitoring/logging infrastructure not shown
- Backup systems not included in diagrams

### Traceability Matrix

```
┌─────────────────────────┬───────────────────────┬──────────────────────────────┐
│ C4 Container            │ Deployment Node        │ Artifact                     │
├─────────────────────────┼───────────────────────┼──────────────────────────────┤
│ Web App [C-01]          │ Client Browser         │ React SPA                    │
│ Mobile App [C-02]       │ Mobile Device          │ React Native App             │
│ Smart TV App [C-03]     │ Smart TV               │ Tizen / webOS App            │
│ API Gateway [C-04]      │ EC2 (Kong)             │ Kong Gateway                 │
│ Streaming Service [C-05]│ EKS Pod                │ streaming-svc:v2.4 (Go)      │
│ User Service [C-06]     │ EKS Pod                │ user-svc:v3.1 (Node.js)      │
│ Catalog Service [C-07]  │ EKS Pod                │ catalog-svc:v1.8 (Node.js)   │
│ Billing Service [C-08]  │ EKS Pod                │ billing-svc:v2.0 (Spring)    │
│ Rec. Engine [C-09]      │ EKS Pod                │ rec-engine:v1.5 (Python/TF)  │
│ Transcoding Worker[C-10]│ EKS Pod                │ transcode-worker:v2.1        │
│ Event Bus [C-11]        │ Amazon MSK             │ Kafka (3 brokers)            │
│ Primary DB [C-12]       │ Amazon RDS             │ PostgreSQL 16 (Multi-AZ)     │
│ Cache [C-13]            │ ElastiCache            │ Redis 7 Cluster              │
│ Video Store [C-14]      │ Amazon S3              │ HLS Segments + Raw Uploads   │
│ Search Index [C-15]     │ Amazon OpenSearch      │ Elasticsearch 8              │
└─────────────────────────┴───────────────────────┴──────────────────────────────┘
```

### Validation Checklist

- [x] All component names match across diagrams
- [x] External entities consistently represented
- [x] Technology choices aligned across views
- [x] Network protocols consistently labeled
- [x] Container-to-node mapping documented
- [x] Assumptions clearly stated
- [x] All required diagrams created and referenced

---

> **Note:** This documentation ensures that anyone reviewing the architecture can understand not just the individual diagrams, but how they work together to provide a complete picture of both the logical application architecture and its physical deployment infrastructure.
