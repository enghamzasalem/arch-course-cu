# Assignment Submission: Lecture 8

**Student Name**: Amaan Shaikh

## Overview

This submission contains the architecture analysis for a **Task Board API**, applying concepts from Chapter 8: Compatibility and Coupling. The analysis includes coupling inventory, change classification, version coexistence strategy, compatibility policy, and migration diagrams.

## Files Included

### Part 1 – Coupling Analysis

- `part1_coupling_analysis.md` — Coupling inventory with 5+ component pairs, coupling types, and ripple effect analysis
- `part1_coupling_diagram.drawio` — Coupling diagram showing dependencies between components (draw.io diagram)
- `part1_coupling_diagram.png` — Coupling diagram (image)

### Part 2 – Compatibility and Versioning

- `part2_compatibility_changes.md` — Classification of 5 changes (A-E) as breaking/non-breaking with semver recommendations
- `part2_version_coexistence.md` — Version coexistence strategy (header-based + path fallback), migration plan, and operational costs

### Part 3 – Policy and Migration

- `part3_compatibility_policy.md` — Compatibility policy covering additive vs breaking changes, deprecation process, error format stability, and partner treatment
- `part3_migration_sequence.drawio` — Migration sequence diagram showing v1 to v2 transition (draw.io diagram)
- `part3_migration_sequence.png` — Migration sequence diagram (image)

### Documentation

- `README.md` — This file

## Key Highlights

- **5 coupling pairs** identified with types: data, control, temporal, deployment
- **2 intentionally tight** (API ↔ Store, Web ↔ Gateway) and **2 to reduce** (Partner ↔ API, API ↔ Notification)
- **Change classification:** A (non-breaking MINOR), B (breaking MAJOR), C (breaking MAJOR), D (breaking MAJOR), E (non-breaking MINOR)
- **Version coexistence:** Header-based versioning with path fallback + 6-month sunset window
- **Compatibility policy:** Clear rules for additive vs breaking changes, deprecation headers, 90/180-day notice periods
- **Migration diagram:** 6 participants showing phased migration from v1 to v2

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files in any text editor or Markdown viewer

## Changes Summary

| Change | Breaking? | Semver | Risk |
|--------|-----------|--------|------|
| A – Add priority field | No | MINOR | Strict schema validators |
| B – Rename done→completed | Yes | MAJOR | All clients break |
| C – Require X-Client-Id | Yes | MAJOR | All requests fail |
| D – Reduce title max length | Yes | MAJOR | Valid data becomes invalid |
| E – Add bulk endpoint | No | MINOR | None |

## System Components

- Web SPA, Mobile App, Partner Integration
- API Gateway
- Task API Service, Task Store, Notification Service
- Database

## Coupling Summary

| Provider | Consumer | Coupling Type |
|----------|----------|---------------|
| Task API | Web SPA | Data + Temporal |
| Task API | Mobile App | Data + Temporal |
| Task API | Partner Integration | Data + Control |
| API Gateway | Task API | Deployment + Temporal |
| Task API | Task Store | Data + Deployment |
| Task API | Notification Service | Control + Temporal |

## Version Coexistence Summary

| Aspect | Choice |
|--------|--------|
| Strategy | Header-based (`X-API-Version`) + path fallback (`/v1`, `/v2`) |
| Sunset period | 6 months |
| v1 behavior | Returns `Deprecation` header after month 3 |
| v1 end | Returns `410 Gone` after sunset |