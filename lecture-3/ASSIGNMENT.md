# Assignment: Architecture Diagramming with Draw.io

## Overview

This assignment requires you to create comprehensive architecture diagrams using **draw.io** (now diagrams.net) for a real-world system. You will apply concepts from **Chapters 1, 2, and 3**, with special focus on **Chapter 3: Definitions and Terminology**.

## Learning Objectives

By completing this assignment, you will:
- Apply architectural terminology and definitions from Chapter 3
- Create multiple views of a system architecture
- Identify components and connectors
- Document architectural decisions
- Understand quality attributes (Chapter 2)
- Apply fundamental architecture concepts (Chapter 1)

## Assignment Scenario

You are an architect tasked with designing and documenting a **Smart Home Management System**. This system allows homeowners to:
- Control smart devices (lights, thermostats, security cameras, door locks)
- Monitor energy consumption
- Receive security alerts
- Schedule automated routines
- Access the system via mobile app, web interface, and voice assistants

## Part 1: System Architecture Design (Chapter 1 & 3)

### Task 1.1: Component and Connector Diagram

**Objective**: Create a component and connector diagram showing the high-level architecture.

**Requirements**:
1. Use draw.io to create a diagram with:
   - **At least 6 components** (e.g., Mobile App, Web Interface, API Gateway, Device Manager, Security Service, Database)
   - **At least 5 connectors** showing how components communicate
   - Clear labels for each component and connector
   - Different shapes/colors for different component types

2. For each component, specify:
   - Component name
   - Component type (Service, Database, Queue, Gateway, etc.)
   - Main responsibilities (2-3 bullet points)

3. For each connector, specify:
   - Connector type (REST API, Message Queue, Database Connection, WebSocket, etc.)
   - Communication protocol
   - Data format

**Deliverable**: `part1_component_connector_diagram.drawio`

**Grading Criteria**:
- Clear component identification (20%)
- Appropriate connector types (20%)
- Correct use of architectural terminology (20%)
- Diagram clarity and organization (20%)
- Completeness (20%)

---

### Task 1.2: Architecture vs. Design Documentation

**Objective**: Distinguish between architectural and design decisions.

**Requirements**:
1. Create a document listing:
   - **5 Architectural Decisions** (strategic, system-wide)
     - Example: "Use microservices architecture for independent scaling"
   - **5 Design Decisions** (tactical, component-level)
     - Example: "Use HashMap for in-memory device cache"

2. For each architectural decision, include:
   - Decision statement
   - Rationale (why this decision)
   - Alternatives considered
   - Consequences

3. For each design decision, include:
   - Decision statement
   - Rationale
   - Design pattern used (if any)
   - Scope (class, method, component)

**Deliverable**: `part1_architecture_vs_design.md`

**Grading Criteria**:
- Clear distinction between architecture and design (30%)
- Quality of architectural decisions (25%)
- Quality of design decisions (25%)
- Documentation completeness (20%)

---

## Part 2: Quality Attributes and Views (Chapter 2 & 3)

### Task 2.1: Quality Attributes Analysis

**Objective**: Identify and prioritize quality attributes for the system.

**Requirements**:
1. Create a document analyzing quality attributes:
   - **List 5 quality attributes** that are most important for this system
   - For each quality attribute:
     - Define it (internal/external, static/dynamic)
     - Explain why it's important for this system
     - Describe how the architecture supports it
     - Identify trade-offs made

2. Create a **quality attribute priority matrix** showing:
   - Which attributes are most critical
   - Which attributes might conflict
   - How you balanced competing attributes

**Deliverable**: `part2_quality_attributes.md`

**Grading Criteria**:
- Correct identification of quality attributes (25%)
- Understanding of internal/external, static/dynamic (25%)
- Architecture support for quality attributes (25%)
- Trade-off analysis (25%)

---

### Task 2.2: Multiple Views Diagram

**Objective**: Create different views of the same system for different stakeholders.

**Requirements**:
1. Create **3 different views** using draw.io:

   **a) Logical View** (for Developers and Architects)
   - Show functional components and their relationships
   - Focus on "what" the system does
   - Include: Components, Interfaces, Services

   **b) Physical/Deployment View** (for DevOps)
   - Show deployment architecture and infrastructure
   - Focus on "where" components are deployed
   - Include: Servers, Networks, Databases, Cloud services

   **c) Scenarios/Sequence View** (for Product Managers and Testers)
   - Show how the system handles a specific use case
   - Focus on "how" components interact
   - Include: User actions, Component interactions, Data flow
   - Choose one scenario: "User turns on lights via mobile app"

2. For each view, include:
   - Title and viewpoint name
   - Legend explaining symbols
   - Brief description of what the view shows
   - Target stakeholder(s)

**Deliverable**: `part2_multiple_views.drawio` (one file with multiple pages/tabs)

**Grading Criteria**:
- Correct use of viewpoints (30%)
- Appropriate content for each view (30%)
- Clarity and organization (20%)
- Stakeholder appropriateness (20%)

---

## Part 3: Architectural Patterns and Decisions (Chapter 3)

### Task 3.1: Architectural Pattern Selection

**Objective**: Choose and document an architectural pattern.

**Requirements**:
1. Select **one architectural pattern** for your system:
   - Options: Layered, MVC, Microservices, Event-Driven, Client-Server
   - Or propose a hybrid approach

2. Create a diagram in draw.io showing:
   - How your system follows the chosen pattern
   - Pattern-specific components
   - Pattern-specific connectors
   - Annotations explaining pattern elements

3. Write a justification document explaining:
   - Why you chose this pattern
   - How it addresses system requirements
   - What trade-offs you made
   - Alternative patterns considered

**Deliverable**: 
- `part3_architectural_pattern.drawio`
- `part3_pattern_justification.md`

**Grading Criteria**:
- Correct application of pattern (30%)
- Justification quality (30%)
- Trade-off analysis (20%)
- Diagram clarity (20%)

---

### Task 3.2: Architectural Decision Records (ADRs)

**Objective**: Document architectural decisions using ADR format.

**Requirements**:
1. Create **3 Architectural Decision Records (ADRs)** for your system:

   **ADR 1**: Choose a major architectural decision (e.g., microservices vs. monolith)
   **ADR 2**: Choose a technology decision (e.g., database choice, messaging system)
   **ADR 3**: Choose a deployment decision (e.g., cloud provider, containerization)

2. For each ADR, use this format:
   ```markdown
   # ADR-001: [Title]
   
   ## Status
   [Accepted/Proposed/Deprecated]
   
   ## Context
   [Why this decision is needed]
   
   ## Decision
   [What was decided]
   
   ## Consequences
   - [Positive consequence]
   - [Negative consequence]
   - [Neutral consequence]
   
   ## Alternatives Considered
   - [Alternative 1]: [Why not chosen]
   - [Alternative 2]: [Why not chosen]
   ```

**Deliverable**: `part3_architectural_decisions.md`

**Grading Criteria**:
- ADR format completeness (25%)
- Quality of context and rationale (30%)
- Consequences analysis (25%)
- Alternatives consideration (20%)

---

## Part 4: Technical Debt and Smells (Chapter 3)

### Task 4.1: Technical Debt Analysis

**Objective**: Identify potential technical debt in your architecture.

**Requirements**:
1. Create a document identifying:
   - **3 potential technical debt items** in your design
   - For each item:
     - Description
     - Type (Architectural, Code, Test, Documentation, Dependency)
     - Severity (Low, Medium, High, Critical)
     - Principal (cost to fix)
     - Interest (ongoing cost)
     - Impact

2. Create a **technical debt backlog** prioritizing items by:
   - Interest rate (ongoing cost)
   - Impact on system
   - Effort to fix

**Deliverable**: `part4_technical_debt.md`

**Grading Criteria**:
- Identification of realistic debt items (30%)
- Understanding of principal vs. interest (30%)
- Prioritization rationale (20%)
- Documentation quality (20%)

---

### Task 4.2: Architectural Smells Detection

**Objective**: Identify architectural smells in your design.

**Requirements**:
1. Review your architecture and identify:
   - **2 potential architectural smells**
   - Common smells: God Component, Circular Dependencies, Scattered Concerns, Tangled Dependencies

2. For each smell:
   - Name the smell
   - Describe where it appears in your architecture
   - Explain why it's a problem
   - Propose a solution to eliminate it
   - Create a diagram showing the "before" and "after" refactoring

**Deliverable**: 
- `part4_architectural_smells.md`
- `part4_smell_refactoring.drawio`

**Grading Criteria**:
- Correct identification of smells (30%)
- Problem understanding (25%)
- Solution quality (25%)
- Refactoring diagram clarity (20%)

---

## Submission Requirements

### Submission Method: Pull Request (PR)

**All submissions must be made via GitHub Pull Request.**

### File Structure

Your submission should have the following structure in your fork:

```
assignment_submission/
├── part1_component_connector_diagram.drawio
├── part1_component_connector_diagram.png          # Exported image
├── part1_architecture_vs_design.md
├── part2_quality_attributes.md
├── part2_multiple_views.drawio
├── part2_multiple_views.png                      # Exported image
├── part3_architectural_pattern.drawio
├── part3_architectural_pattern.png               # Exported image
├── part3_pattern_justification.md
├── part3_architectural_decisions.md
├── part4_technical_debt.md
├── part4_architectural_smells.md
├── part4_smell_refactoring.drawio
├── part4_smell_refactoring.png                   # Exported image
├── code/                                         # Optional: supporting code
│   ├── component_examples.py
│   ├── connector_examples.py
│   └── architecture_models.py
└── README.md                                     # Your submission summary
```

### Draw.io Files and Images

**IMPORTANT**: You must submit BOTH:
1. **`.drawio` files** - The editable source files
2. **`.png` files** - Exported images of your diagrams

**How to Export Draw.io Diagrams as Images:**

1. Open your diagram in draw.io
2. Go to **File → Export as → PNG**
3. Choose settings:
   - **Zoom**: 200% (for high quality)
   - **Border**: 10px
   - **Transparent Background**: Optional
4. Save with the same name as your `.drawio` file (e.g., `part1_component_connector_diagram.png`)
5. Include both files in your submission

### Documentation Files

- All `.md` files should use Markdown format
- Use clear headings and structure
- **Reference your diagram images** using Markdown image syntax: `![Description](part1_component_connector_diagram.png)`
- Write professionally but concisely

### Code Files (Optional but Recommended)

If you create code examples to support your architecture:
- Place all code in the `code/` directory
- Use clear, commented code
- Include a brief explanation in your README.md
- Code should demonstrate architectural concepts from Chapters 1, 2, and 3

---

## Grading Rubric

### Overall Assignment (100 points)

| Part | Task | Points |
|------|------|--------|
| Part 1 | Component & Connector Diagram | 15 |
| Part 1 | Architecture vs. Design | 10 |
| Part 2 | Quality Attributes Analysis | 15 |
| Part 2 | Multiple Views Diagram | 15 |
| Part 3 | Architectural Pattern | 15 |
| Part 3 | ADRs | 10 |
| Part 4 | Technical Debt Analysis | 10 |
| Part 4 | Architectural Smells | 10 |

### Quality Criteria

- **Terminology (20%)**: Correct use of architectural terms from Chapter 3
- **Completeness (20%)**: All requirements met
- **Clarity (20%)**: Diagrams and documents are clear and well-organized
- **Understanding (20%)**: Demonstrates understanding of concepts
- **Creativity (10%)**: Thoughtful application of concepts
- **Professionalism (10%)**: Well-formatted, error-free submission

---

## Getting Started with Draw.io

### Access Draw.io

1. Go to [https://app.diagrams.net/](https://app.diagrams.net/) (or [https://draw.io](https://draw.io))
2. Choose where to save your diagrams (Google Drive, OneDrive, or Device)
3. Start with a blank diagram or use a template

### Tips for Architecture Diagrams

1. **Use Appropriate Shapes**:
   - Rectangles for components/services
   - Cylinders for databases
   - Clouds for external systems
   - Arrows for connectors/relationships

2. **Organize Your Diagram**:
   - Use layers for different concerns
   - Group related components
   - Use consistent colors (e.g., blue for services, green for databases)
   - Add legends to explain symbols

3. **Label Everything**:
   - Component names
   - Connector types
   - Data flows
   - Relationships

4. **Keep It Clear**:
   - Don't overcrowd the diagram
   - Use multiple diagrams if needed
   - Use pages/tabs for different views

### Draw.io Resources

- [Draw.io Tutorial](https://www.diagrams.net/blog/draw-io-tutorial)
- [Architecture Diagram Examples](https://www.diagrams.net/blog/architecture-diagrams)
- [Shape Libraries](https://www.diagrams.net/blog/shape-libraries)

---

## Example: Component and Connector Diagram

Here's a simple example to get you started:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Mobile App │────────▶│  API Gateway │────────▶│ User Service│
└─────────────┘  HTTPS  └──────────────┘  REST  └─────────────┘
                                                         │
                                                         │ SQL
                                                         ▼
                                                  ┌─────────────┐
                                                  │   Database  │
                                                  └─────────────┘
```

In draw.io, you would:
1. Create rectangles for components
2. Add arrows for connectors
3. Label each element
4. Use colors to distinguish types
5. Add a legend

---

## Important Notes

1. **Be Realistic**: Your architecture doesn't need to be perfect, but it should be realistic and well-thought-out.

2. **Show Your Thinking**: Document your reasoning, not just your decisions.

3. **Use Terminology**: Use the correct architectural terminology from Chapter 3.

4. **Ask Questions**: If you're unsure about requirements, ask your instructor.

5. **Start Early**: This assignment requires multiple diagrams and documents. Start early and iterate.

6. **Review Examples**: Look at the example files in `lecture-3/` for inspiration.

---

## Submission Process via Pull Request

### Step 1: Fork the Repository

1. Fork the course repository to your GitHub account
2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/arch-course-cu.git
   cd arch-course-cu
   ```

### Step 2: Create Your Submission Branch

```bash
git checkout -b assignment-lecture3-YOUR_NAME
# Example: assignment-lecture3-john-doe
```

### Step 3: Create Your Submission Directory

```bash
mkdir -p arch-course-cu/lecture-3/submissions/YOUR_NAME
cd arch-course-cu/lecture-3/submissions/YOUR_NAME
```

### Step 4: Complete Your Assignment

1. Create all required files in your submission directory
2. Export all draw.io diagrams as PNG images
3. Include both `.drawio` and `.png` files
4. Add any supporting code to a `code/` subdirectory
5. Create a `README.md` with your submission summary

### Step 5: Commit and Push

```bash
git add .
git commit -m "Submit Lecture 3 Assignment - [Your Name]"
git push origin assignment-lecture3-YOUR_NAME
```

### Step 6: Create Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template (see below)
5. Submit the PR

### PR Title Format

```
[Assignment] Lecture 3 - [Your Name]
```

Example: `[Assignment] Lecture 3 - John Doe`

### PR Description Template

```markdown
## Assignment Submission: Lecture 3

**Student Name**: [Your Name]
**Student ID**: [Your ID]
**Date**: [Submission Date]

### Submission Checklist

- [x] Part 1: Component and Connector Diagram (drawio + png)
- [x] Part 1: Architecture vs. Design Documentation
- [x] Part 2: Quality Attributes Analysis
- [x] Part 2: Multiple Views Diagram (drawio + png)
- [x] Part 3: Architectural Pattern Diagram (drawio + png)
- [x] Part 3: Pattern Justification
- [x] Part 3: Architectural Decision Records (3 ADRs)
- [x] Part 4: Technical Debt Analysis
- [x] Part 4: Architectural Smells Detection (drawio + png)
- [x] All diagrams exported as PNG images
- [x] README.md with submission summary

### Notes

[Any additional notes or explanations about your submission]

### Code Examples

[If you included code, briefly describe what it demonstrates]
```

## Submission Deadline

**Due Date**: [To be announced by instructor]

**Submission Method**: GitHub Pull Request (PR)

**Late Policy**: 
- Late submissions will be accepted with a 10% penalty per day
- Maximum 3 days late
- PRs submitted after the deadline will be marked accordingly

---

## Academic Integrity

- This is an individual assignment. You may discuss concepts with classmates but must create your own diagrams and documents.
- Cite any external resources you use.
- Do not copy diagrams or text from other sources without proper attribution.

---

## Questions?

If you have questions about:
- **Requirements**: Check this document first, then ask your instructor
- **Draw.io Usage**: Check the Draw.io documentation and tutorials
- **Architectural Concepts**: Review Chapter 1, 2, and 3 materials
- **Examples**: Review the example files in `lecture-3/`

---

## Good Luck! 🚀

This assignment is designed to help you apply what you've learned about software architecture. Take your time, think through your decisions, and create clear, professional diagrams and documentation.

