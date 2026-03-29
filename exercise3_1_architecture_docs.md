Architecture Documentation: Simple Blog System
1. System Overview
The Simple Blog System is a web application that allows authors to publish markdown-based articles and allows readers to view those articles and leave comments.


2.Logical View (What the system does)
Purpose: This view illustrates the system from the perspective of the end-users and the high-level functional boundaries. It ignores technology choices (like Python vs. Node.js) and focuses purely on business capabilities.

+----------------+       +---------------------------------------------+
|                |       |  Simple Blog System                         |
|   [Reader]     |------>|  - View published articles                  |
|                |       |  - Search articles by tag                   |
+----------------+       |  - Post comments                            |
                         |                                             |
+----------------+       |                                             |
|                |       |                                             |
|   [Author]     |------>|  - Write/Edit/Delete articles (Drafts)      |
|                |       |  - Publish articles                         |
+----------------+       |  - Moderate comments                        |
                         +---------------------------------------------+

**Key Relationships**

Reader: Interacts with the public-facing reading and commenting capabilities.

Author: Interacts with the restricted, authenticated authoring capabilities.

Capabilities: The system is fundamentally split into "Content Consumption" and "Content Management".


**3.Component View (How the system is structured)**
Purpose: This view breaks the system down into its major software components (the "building blocks"). It shows the interfaces between them and how data flows. This is the view developers care about most.


[Web Browser / Client]
                |
                | (JSON over HTTPS)
                v
+---------------------------------------+
|          [API Gateway / Router]       | <-- Routes requests
+---------------------------------------+
        |                       |
        v                       v
+---------------+       +---------------+
|  Auth System  |       | Content API   | <-- Core Business Logic
| (Validates JWT|       | (Gets articles|
|  tokens)      |       |  adds comments|
+---------------+       +---------------+
        |                       |
        +-----------+-----------+
                    | (SQL Queries)
                    v
            [(SQL Database)] <-- Data Persistence


**Key Components**

- API Gateway: The single entry point for all client requests. It handles rate limiting and routing.

- Auth System: A dedicated component (implementing the Single Responsibility Principle) that verifies if an Author is logged in.

- Content API: The core service. It orchestrates fetching articles, saving drafts, and appending comments.

- SQL Database: The persistent storage layer holding tables for Users, Articles, and Comments.


**4.Deployment View (Where the system runs)**
Purpose: This view shows the physical (or virtual) hardware infrastructure. It details how the software components from the Component View are mapped onto servers, containers, or cloud services. This is the view DevOps and Site Reliability Engineers (SREs) care about.


[User's Laptop/Phone]
        |
        | (Internet / DNS: blog.example.com)
        v
+-----------------------------------------------------------
|  Cloud Provider (e.g., AWS / Google Cloud)                |
|                                                           |
|  +--------------------+                                   |
|  |  [Load Balancer]   |                                   |
|  +--------------------+                                   |
|           |                                               |
|           v                                               |
|  +--------------------+       +--------------------+      |
|  | [Web Server Node 1]|       | [Web Server Node 2]|      |
|  | (Runs Content API) |       | (Runs Content API) |      |
|  +--------------------+       +--------------------+      |
|           |                              |                |
|           +--------------+---------------+                |
|                          |                                |
|                          v                                |
|               [(Managed PostgreSQL DB)]                   |
|               (Primary with auto-backups)                 |
+-----------------------------------------------------------+



**Key Deployment Decisions**

- Redundancy: We deploy two instances of the Web Server Node behind a Load Balancer. If Node 1 crashes, Node 2 keeps the blog online (High Availability).

- Managed Database: Instead of installing a database on the web servers, we use a managed cloud database. This separates the storage from the computing power, making the system easier to scale.


**Why Multiple Views Matter**

A developer wouldn't know if they should create a web server or a mobile application if you just gave them the Logical View.
They would be aware that they are utilizing AWS and PostgreSQL if you merely displayed the Deployment View, but they would be unaware of the true purpose of the application for the users!

You may present a comprehensive image of the architecture by integrating different perspectives.


