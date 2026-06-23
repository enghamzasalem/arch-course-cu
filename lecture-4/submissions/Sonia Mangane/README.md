# Assignment Submission: Lecture 3

**Student Name**: Sonia Mangane  
**Student ID**:  
**Submission Date**: 05 March 2026  

---

# Overview

This submission presents the architectural modeling of a **Video Streaming Platform** using the **C4 Model** and supporting UML diagrams.  
The objective was to model the system from high-level context down to internal components while maintaining consistency across diagrams.

The architecture demonstrates how users interact with the platform, how services communicate internally, and how external systems such as payment processing and content delivery networks integrate with the system.

---

# Files Included

### Diagrams

- **part1_context_diagram.drawio**  
  Editable C4 Level 1 System Context diagram showing users and external systems interacting with the platform.

- **part1_context_diagram.png**  
  Exported image version of the context diagram.

- **part1_container_diagram.drawio**  
  C4 Level 2 container diagram showing the main application components and technology stack.

- **part1_container_diagram.png**  
  Exported image of the container architecture.

- **part1_component_diagram.drawio**  
  C4 Level 3 component diagram focusing on the API Backend container.

- **part1_component_diagram.png**  
  Exported image of the API component structure.

---

### Documentation

- **architecture_documentation.md**  
  Contains the modeling approach, diagram explanations, consistency checks, assumptions, and references.

---

# Key Highlights

- Implementation of the **C4 Model (Levels 1–3)** 
- Clear separation of **users, containers, and external systems** such as CDN, Payment Gateway, and Notification Service.
- Consistent architectural naming and relationships across all diagrams to maintain a **single source of truth**.

---

# How to View

1. Open the `.drawio` files using **draw.io / diagrams.net** to view and edit the architecture diagrams.
2. View the `.png` files for quick visual reference without editing.
3. Read the `.md` files for architectural explanations and documentation.
4. Ensure all diagrams and documentation are kept together in the same project folder for correct referencing.

---

# Viewing Diagrams in Markdown

Images can be embedded inside Markdown documentation using the following syntax:


```markdown
![System Context Diagram](part1_context_diagram.drawio.png)

![Container Diagram](part1_container_diagram.drawio.png)

![API Component Diagram](part1_component_diagram.drawio.png)

![Deployment Diagram](part2_deployment_diagram.drawio.png)

![Sequence Diagram](part2_sequence_diagram.drawio.png)




