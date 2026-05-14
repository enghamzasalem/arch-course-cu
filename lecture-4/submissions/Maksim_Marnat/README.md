# Lecture 4 Assignment — Video Streaming Platform (Maksim_Marnat)

Architecture modeling submission: C4 model (Context, Container, Component) and UML (Sequence, Deployment) for a Netflix-style video streaming platform.

## Contents

| File | Description |
|------|-------------|
| `part1_context_diagram.drawio` | C4 Level 1 — System context (users, system, external systems) |
| `part1_container_diagram.drawio` | C4 Level 2 — Containers (Web, Mobile, TV, API, Recommendation, Streaming, DB, Cache) |
| `part1_component_diagram.drawio` | C4 Level 3 — API Gateway decomposed into 6 components |
| `part2_sequence_diagram.drawio` | UML Sequence — Use case "User watches a video" (5 participants, 9 messages) |
| `part2_deployment_diagram.drawio` | UML Deployment — 4+ nodes, artifacts, stereotypes |
| `part3_model_documentation.md` | Modeling approach, diagram index, consistency check |

## PNG export (optional)

PNG files are not included. If required for submission, open each `.drawio` in [draw.io](https://app.diagrams.net/), then **File → Export as → PNG** (200% zoom).

## Scenario

- **System:** Video Streaming Platform (browse, search, stream, watchlist, history, recommendations; web, mobile, smart TV).
- **Users:** Subscriber, Content Creator, Admin.
- **External:** Payment Gateway, CDN.

## Checklist vs assignment

- [x] Part 1.1: Context — 1 system, 3 users, 2 external systems, labeled relationships
- [x] Part 1.2: Container — 5+ containers, technology labels, connections with protocol/data format, legend
- [x] Part 1.3: Component — One container (API Gateway) with 4+ components, dependencies
- [x] Part 2.1: Sequence — One use case, 5+ participants, 8+ messages, title and description
- [x] Part 2.2: Deployment — 4+ nodes, artifacts, connections, stereotypes, brief infrastructure description
- [x] Part 3: Model documentation — Approach, diagram index, consistency check, image references

**Note:** This is a draft submission; not sent via PR. Export PNGs and open a PR when ready to submit.
