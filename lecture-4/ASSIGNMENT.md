# Assignment: Architecture Modeling with C4 and UML

## Overview

This assignment requires you to create architecture models and diagrams using **draw.io** for a real-world system. You will apply concepts from **Chapter 4: Modeling Software Architecture**, including the C4 model, UML diagrams, and architecture documentation.

## Learning Objectives

By completing this assignment, you will:
- Apply the C4 model (Context, Container, Component levels)
- Create UML diagrams (Component, Deployment, Sequence)
- Document architecture using standard modeling notations
- Communicate architecture effectively for different audiences
- Maintain consistent documentation across diagram levels

## Assignment Scenario

You are an architect tasked with modeling a **Video Streaming Platform** (e.g., Netflix-style). The system allows users to:
- Browse and search video content
- Stream videos with adaptive quality
- Manage watchlists and viewing history
- Get personalized recommendations
- Access via web, mobile app, and smart TV

## Part 1: C4 Model Diagrams

### Task 1.1: System Context Diagram (C4 Level 1)

**Objective**: Create a system context diagram showing the system boundary and external actors.

**Requirements**:
1. Use draw.io to create a diagram with:
   - **1 system** (the video streaming platform)
   - **At least 3 users/persons** (e.g., Subscriber, Content Creator, Admin)
   - **At least 2 external systems** (e.g., Payment Gateway, CDN)
   - **Labeled relationships** showing how they interact

2. Follow C4 notation:
   - Person (stick figure or person icon) for users
   - Box for your system
   - Box for external systems
   - Arrows with labels for relationships

3. Add a brief description of each relationship

**Deliverables**: 
- `part1_context_diagram.drawio`
- `part1_context_diagram.png`

**Grading**: 15 points

---

### Task 1.2: Container Diagram (C4 Level 2)

**Objective**: Create a container diagram showing the high-level software architecture.

**Requirements**:
1. Create a diagram with:
   - **At least 5 containers** (e.g., Web App, Mobile App, API, Recommendation Service, Database)
   - **Technology labels** for each container (e.g., [React], [PostgreSQL])
   - **Connections** showing how containers communicate
   - **Protocol/data format** labels on connections

2. Each container should have:
   - Clear name
   - Technology stack
   - Main responsibility (1-2 sentences)

3. Include a legend explaining your notation

**Deliverables**: 
- `part1_container_diagram.drawio`
- `part1_container_diagram.png`

**Grading**: 20 points

---

### Task 1.3: Component Diagram (C4 Level 3)

**Objective**: Create a component diagram for ONE container (e.g., API or Recommendation Service).

**Requirements**:
1. Pick one container from Task 1.2
2. Decompose it into **at least 4 components**
3. Show:
   - Component names and responsibilities
   - Dependencies between components
   - Key interfaces (if applicable)
4. Use consistent notation (boxes, arrows)

**Deliverables**: 
- `part1_component_diagram.drawio`
- `part1_component_diagram.png`

**Grading**: 15 points

---

## Part 2: UML Diagrams

### Task 2.1: Sequence Diagram

**Objective**: Create a sequence diagram for a key use case.

**Requirements**:
1. Choose ONE use case: "User watches a video" OR "User gets recommendations"
2. Create a sequence diagram showing:
   - **At least 5 participants** (actors, components, or services)
   - **At least 8 messages** in logical order
   - **Sync vs async** distinction (if applicable)
   - **Return messages** where appropriate

3. Use UML sequence notation:
   - Lifelines (vertical lines)
   - Messages (horizontal arrows)
   - Activation bars (optional)
   - Consider: alt/opt frames for alternatives (optional)

4. Add a title and brief description

**Deliverables**: 
- `part2_sequence_diagram.drawio`
- `part2_sequence_diagram.png`

**Grading**: 20 points

---

### Task 2.2: Deployment Diagram

**Objective**: Create a deployment diagram showing infrastructure.

**Requirements**:
1. Create a diagram showing:
   - **At least 4 nodes** (e.g., Web Server, App Server, Database Server, CDN)
   - **Artifacts** deployed on each node
   - **Connections** between nodes (network)
   - **Stereotypes or labels** (e.g., <<cloud>>, <<on-premise>>)

2. Show where your containers from Part 1 run
3. Include a brief infrastructure description

**Deliverables**: 
- `part2_deployment_diagram.drawio`
- `part2_deployment_diagram.png`

**Grading**: 15 points

---

## Part 3: Architecture Documentation

### Task 3.1: Model Documentation

**Objective**: Document your modeling approach and diagram relationships.

**Requirements**:
1. Create a document (`part3_model_documentation.md`) that includes:

   **a) Modeling Approach**
   - Which modeling notations you used (C4, UML)
   - Why you chose these notations
   - How the diagrams relate to each other

   **b) Diagram Index**
   - Table listing all diagrams with: Name, Type, Purpose, Audience

   **c) Consistency Check**
   - How you ensured consistency across diagrams (e.g., same component names)
   - Any assumptions or simplifications made

2. **Embed or reference** your diagram images in the document

**Deliverable**: `part3_model_documentation.md`

**Grading**: 15 points

---

## Submission Requirements

### Submission Method: Pull Request (PR)

**All submissions must be made via GitHub Pull Request.** (See `../lecture-3/SUBMISSION_GUIDE.md` for PR process)

### File Structure

```
submissions/YOUR_NAME/
├── part1_context_diagram.drawio
├── part1_context_diagram.png
├── part1_container_diagram.drawio
├── part1_container_diagram.png
├── part1_component_diagram.drawio
├── part1_component_diagram.png
├── part2_sequence_diagram.drawio
├── part2_sequence_diagram.png
├── part2_deployment_diagram.drawio
├── part2_deployment_diagram.png
├── part3_model_documentation.md
└── README.md
```

### Draw.io and Images

- Submit **both** `.drawio` (source) and `.png` (exported image) for each diagram
- Export at 200% zoom for quality
- Reference images in markdown: `![Description](filename.png)`

---

## Grading Rubric

| Part | Task | Points |
|------|------|--------|
| Part 1 | Context Diagram (C4 L1) | 15 |
| Part 1 | Container Diagram (C4 L2) | 20 |
| Part 1 | Component Diagram (C4 L3) | 15 |
| Part 2 | Sequence Diagram | 20 |
| Part 2 | Deployment Diagram | 15 |
| Part 3 | Model Documentation | 15 |
| **Total** | | **100** |

### Quality Criteria

- **Correct Notation (25%)**: Proper use of C4 and UML conventions
- **Completeness (25%)**: All required elements present
- **Clarity (25%)**: Diagrams are readable and well-organized
- **Consistency (15%)**: Diagrams align with each other
- **Documentation (10%)**: Clear explanations and rationale

---

## Getting Started

1. **Review the examples** in `lecture-4/example1_c4_model_and_diagrams.py` and `example2_uml_and_sequence_diagrams.py`
2. **Use draw.io**: https://app.diagrams.net/
3. **C4 reference**: https://c4model.com/
4. **Follow the submission guide** in lecture-3 for PR process

---

## Important Notes

- Be realistic but you may simplify for the assignment
- Use consistent naming across all diagrams
- Focus on clarity over complexity
- Cite any external references you use

---

## Deadline

**Due Date**: next week lecture 

**Submission**: GitHub Pull Request to `arch-course-cu/lecture-4/submissions/YOUR_NAME/`

Good luck! 🚀
