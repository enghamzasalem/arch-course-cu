Task 3.2: Architectural Decision Records (ADRs)

**ADR-001: Adoption of Microservices Architecture over a Monolithic Approach**

**Status**: Accepted

**Context:** The Smart Home Management System needs to support heterogeneous workloads with high-frequency device telemetry for energy monitoring, sudden increases in security event rates from motion detection systems, and varying traffic rates from device control systems. It needs to scale independently across functional domains while being adaptable to new device types that are introduced annually. A single deployment unit would create scalability and maintenance issues.

**Decision:** The Smart Home Management System will be decomposed into domain-oriented micro services: Device Management, Security & Alerts, Energy Monitoring, and Notifications. These will be hosted behind an API Gateway and communicate with each other via RESTful APIs and message queues.

**Consequences:**

**Positive:** It will enable the Smart Home Management System to scale independently across domains (e.g., Security during event spikes, Energy during reporting).It will enable Fault Isolation and team autonomy for each microservice.

**Negative:** It will introduce the complexity associated with distributed systems (network latency and eventual consistency).It will introduce operational complexity due to multiple services.

**Neutral:** Development costs will increase. Evolvability will improve significantly.

**Alternatives Considered:** A Monolithic Application. A Modular Monolith**.** A Serverless Architecture

**ADR-002: Adoption of PostgreSQL as the Primary System Database**

**Status:** Accepted

**Context:** The system requires a relational database to manage entities such as users, households, devices, and routines, with complex interrelations and transactional consistency. Additionally, the system requires features to handle time-series data for energy metrics. For the minimum viable product (MVP) stage, simplicity and lower operational cost are considered essential.

**Decision:** Adopt PostgreSQL with TimescaleDB as an extension to handle time-series data. The database will be the single primary database to handle configuration data, audit logs, and time-series data for energy metrics.

**Consequences:**

**Positive:** The system can handle ACID transactions for users, devices, and routines. Additionally, it can handle high volumes of metrics with the TimescaleDB extension. The system can leverage an established ecosystem and robust tooling.

**Negative:** The system can suffer from coupling between services, as it is using a single database. The system can suffer from scalability issues, as it is using a single database.

**Neutral:** The system can suffer from higher operational costs, as it is not using cloud databases. The system can have more control and portability, as it is not using cloud databases.

**Alternatives Considered**

- **Separate databases for each service (one database per microservice):** The system can have more autonomy for each service. The system can suffer from distributed transaction issues and data consistency.
- **MongoDB (NoSQL):** The system can have more flexibility with MongoDB. The system can suffer from limitations in supporting relational queries and maintaining device state with eventual consistency.
- **Cassandra:** The system can have more scalability with Cassandra. The system can suffer from limitations in supporting ACID transactions and can have more complexity, which is not suitable for the MVP stage.

**ADR-003: Deploy to Kubernetes on AWS EKS**

**Status:** Accepted

**Context:** We require services that can autoscale horizontally on their own, deploy without any downtime, perform health checks, and discover other services. The DevOps approach demands Infrastructure as Code, good monitoring, and the ability to deploy across multiple regions for high availability. We are constrained by initial cloud costs.

**Decision:** We choose to deploy the microservices as containerized applications on Kubernetes, which is provided by AWS through its service called EKS (Elastic Kubernetes Service). This deployment will include an Application Load Balancer, RDS for PostgreSQL, and CloudWatch for monitoring.

**Consequences**

**Positive:** We get the benefits of autoscaling, rolling updates, self-healing, and service mesh. We get the benefits of the mature AWS platform, which allows us to get high availability across multiple regions.

**Negative:** There is the learning curve associated with Kubernetes, which is an additional operational overhead. We are locked into the AWS platform and have the potential for higher costs than other PaaS solutions.

**Neutral:** We get the benefits of the large community and the availability of skills, which offset the learning curve.

**Alternative Options Considered**

- Docker Compose + EC2
- AWS ECS Fargate
- Heroku/Vercel