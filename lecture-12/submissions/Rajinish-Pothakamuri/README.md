# Assignment Submission: Lecture 12

**Student Name**: Rajinish Pothakamuri  
**Student ID**: 30009056  
**Submission Date**: 15-05-2026 

## Overview

This assignment documents the architectural strategy for splitting the CityBite monolith into a flexible, microservices-based architecture. Drawing on the principles of flexibility and modularity, the design prioritizes high team autonomy and independent deployment lifecycles while carefully avoiding the pitfalls of a "distributed monolith". The strategy utilizes Domain-Driven Design to establish bounded contexts, enforces the database-per-service rule to decouple data, implements the Saga pattern for cross-context transactions, and relies on the Strangler Fig and Branch by Abstraction patterns to ensure a safe, incremental migration.

## Files Included

- **part1_contexts_conway.md**: Defines the bounded contexts (Ordering, Kitchen, Dispatch, Notifications) with their ubiquitous language, defines synchronous/asynchronous integration boundaries, and discusses team structuring via Conway's Law.
- **part1_distributed_monolith.md**: An evaluation of three major microservice anti-patterns (release trains, shared databases, and chatty RPCs) along with their architectural and process mitigations.
- **part2_database_per_service.md**: Logical database schemas enforcing data isolation, a CQRS-based mitigation for lost cross-context join queries, and RPO/RTO implications for asynchronous replication.
- **part2_api_evolution.md**: Documentation on maintaining backward compatibility via additive JSON changes, handling breaking changes with versioning, and using consumer-driven contract tests.
- **part2_saga_sketch.md**: An orchestration-based Saga design mapping the "Place Paid Order" workflow across the Ordering, Payment, and Kitchen contexts, complete with compensating transactions.
- **part3_strangler_plan.md**: A risk-mitigated migration plan utilizing an API Gateway for Strangler Fig traffic routing and internal Branch by Abstraction to safely extract the Payment Context.
- **part3_contexts_current_vs_target.drawio / .png**: Visual representation comparing the current legacy monolithic deployment to the target distributed microservices architecture, highlighting the specific sync/async communication edges.

## Key Highlights

- **Strategic Service Boundaries**: Transitioning from a single, tightly coupled monolith to isolated bounded contexts aligned strictly with business capabilities rather than technical layers, preventing synchronous cascading failures.
- **Data Decentralization & Sagas**: Abandoning a shared relational database in favor of a database-per-service model, preserving strict data encapsulation. Cross-context workflows are managed via orchestrated sagas with explicit compensating actions to maintain eventual consistency.
- **Incremental Migration**: Shifting away from high-risk, "stop-the-world" rewrites by applying the Strangler Fig pattern to route traffic slices gradually and utilizing Branch by Abstraction to harden code paths before completing the physical network split.

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams mapping the current versus target architecture.
2. View `.png` files for a quick reference of the integration styles and bounded context boundaries.
3. Read `.md` files for full technical documentation, API evolution rules, saga workflows, and architectural justifications.