# Assignment Submission: Lecture 12

**Student Name**: Arda Arslan  
**Student ID**: 30008610  
**Submission Date**: 14/05/2026

## Overview

This assignment documents how CityBite could evolve toward finer-grained services without becoming a distributed monolith.  
It covers bounded contexts and Conway's Law, database per service, public API evolution, a saga sketch for a cross-context flow, a strangler / branch by abstraction migration plan, and a current vs target architecture diagram.

## Files Included

### Part 1 – Contexts & Conway

- `part1_contexts_conway.md` – Bounded context map and Conway's Law prediction  
- `part1_distributed_monolith.md` – Distributed monolith red flags and mitigations  

### Part 2 – Data, APIs, Sagas

- `part2_database_per_service.md` – Database per service design and RPO/RTO intuition  
- `part2_api_evolution.md` – Public API evolution with additive and breaking changes  
- `part2_saga_sketch.md` – Saga sketch for "place paid order" journey  

### Part 3 – Migration & Diagram

- `part3_strangler_plan.md` – Strangler / branch by abstraction plan for Payments extraction  
- `part3_contexts_current_vs_target.drawio` – Current vs target architecture diagram  
- `part3_contexts_current_vs_target.png` – Image version of the diagram  

## Key Highlights

- Identified bounded contexts and integration styles  
- Designed database per service split with event-driven replacement  
- Planned strangler migration with branch by abstraction  

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation