# Assignment Submission: Lecture 8

**Student Name**: Relja Popovic
**Student ID**: 30008800
**Submission Date**: 09/04/2026

## Overview
This submission analyzes compatibility and coupling for a Task Board REST API. It includes a coupling inventory and dependency diagram, classification of breaking vs non-breaking API changes with semver recommendations, a version coexistence plan, a compatibility governance policy, and a migration sequence diagram.

## Files Included
- `part1_coupling_analysis.md`
- `part1_coupling_diagram.drawio`
- `part1_coupling_diagram.png`
- `part2_compatibility_changes.md`
- `part2_version_coexistence.md`
- `part3_compatibility_policy.md`
- `part3_migration_sequence.drawio`
- `part3_migration_sequence.png`
- `README.md`

## Key Highlights
- Identified **5 dependency pairs**
- Classified **5 proposed changes** (A–E) as breaking or non-breaking with semver bumps and semantic risks
- Chose a **path-based versioning** for clean client separation during migration
- Defined a **90/180-day deprecation period** for first-party apps/partner integrations