# Assignment Submission: Lecture 8

**Student Name**: Arda Arslan
**Student ID**: 30008610
**Submission Date**: 09/04/2026

## Overview
This submission analyzes compatibility and coupling for a Task Board REST API. It includes a coupling inventory and dependency diagram, classification of breaking vs non-breaking API changes with semver recommendations, a version coexistence plan, a compatibility governance policy, and a migration sequence diagram.

## Files Included
- `part1_coupling_analysis.md` — Coupling inventory with dependency directions, coupling types, and ripple effect analysis
- `part1_coupling_diagram.drawio` — Coupling and dependency diagram (draw.io)
- `part1_coupling_diagram.png` — Coupling and dependency diagram (image)
- `part2_compatibility_changes.md` — Classification of proposed changes A–E as breaking or non-breaking with semver and semantic risk
- `part2_version_coexistence.md` — Version coexistence strategy for v1 and v2 during migration
- `part3_compatibility_policy.md` — Compatibility governance policy covering additive changes, deprecation, error stability, and partner treatment
- `part3_migration_sequence.drawio` — Migration sequence diagram (draw.io)
- `part3_migration_sequence.png` — Migration sequence diagram (image)
- `README.md` — This file

## Key Highlights
- Identified **6 dependency pairs** across Web SPA, Mobile, Partner, Gateway, Task API, Task Store, and Notification Service
- Classified all **5 proposed changes** (A–E) as breaking or non-breaking with semver bumps and semantic risks
- Chose **path-based versioning** (/v1 and /v2) for clean client separation during migration
- Defined a **90-day deprecation period** for first-party apps and **180-day** for partner integrations

## How to View
1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation