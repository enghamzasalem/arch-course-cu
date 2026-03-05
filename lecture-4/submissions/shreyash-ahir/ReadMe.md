README: Video Streaming Platform Architecture
Assignment Submission: Assignment 4
Student Name: Hadiya Shreyash Rameshbhai
Student ID: 30009058
Submission Date: 03-03-2026
Overview
This assignment provides a multi-layered architectural design for a Video Streaming Platform (similar to Netflix). The project utilizes the C4 Model to provide hierarchical abstraction for different stakeholders and UML Diagrams for deep-dive technical modeling of system behavior and physical deployment.
Files Included
Part 1: C4 Model (Hierarchical Views)
c4_level1_system_context.drawio / .png: High-level view of users and external system dependencies.
c4_level2_container.drawio / .png: Technical breakdown into web apps, APIs, and databases.
c4_level3_component.drawio / .png: Internal decomposition of the Streaming & Metadata API.
Part 2: UML Detailed Design
uml_sequence_playback.drawio / .png: Detailed logic for the "Secure Video Playback" process.
uml_deployment_view.drawio / .png: Mapping of Docker artifacts to physical infrastructure and load balancers.
Part 3: Documentation & Analysis
architectural_description.md: Detailed breakdown of each diagram's purpose and audience.
consistency_check.md: Documentation on naming standards, assumptions, and cross-diagram integrity.
pattern_justification.md: Reasoning for using the C4 hierarchy over traditional flat modeling.
Key Highlights
Hierarchical Clarity: Uses the C4 "zoom" approach to cater to both non-technical stakeholders and developers.
Consistency-First Design: Strict 1:1 mapping of components across C4 levels and UML views to prevent architectural drift.
Detailed Workflow Modeling: Explicit modeling of complex events like video uploading and authorized streaming.
How to View
Diagrams: Open .drawio files in draw.io to edit or view the source; use .png files for quick previews.
Documentation: All .md files are formatted in Markdown for easy reading in GitHub, VS Code, or any standard text editor.
Hierarchy: It is recommended to view the C4 diagrams in order (Level 1 through Level 3) to understand the system's drill-down logic.
