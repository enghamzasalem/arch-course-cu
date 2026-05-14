# Assignment Submission: Lecture 3

**Student Name**: Kagontle Booysen  
**Student ID**: 30009255 
**Submission Date**: 30 March 2026

## Overview

This submission analyses how a Task Board REST API and its clients stay maintainable under change. It covers coupling identification and dependency mapping (Part 1), compatibility classification and version coexistence planning for five proposed API changes (Part 2), and a governance policy with migration sequence diagram (Part 3). All work applies Chapter 8 concepts: coupling types, breaking vs non-breaking changes, semantic versioning, and v1/v2 coexistence strategy.

## Files Included

| File | Description |
|------|-------------|
| `part1_coupling_analysis.md` | Coupling inventory for all 7 system elements — direction, type, ripple risk, tight/reduce recommendations |
| `part1_coupling_diagram.drawio` | Editable dependency diagram with coupling labels and legend |
| `part1_coupling_diagram.png` | PNG export of the coupling diagram for quick reference |
| `part2_compatibility_changes.md` | Change classification for A–E: breaking vs non-breaking, semver bump, semantic risk per change |
| `part2_version_coexistence.md` | v1/v2 coexistence plan — path prefix strategy, routing design, sunset timeline, operational cost |
| `part3_compatibility_policy.md` | Compatibility governance policy — additive vs breaking rules, deprecation process, error format stability, partner vs first-party treatment |
| `part3_migration_sequence.drawio` | Editable sequence diagram showing partner migration from v1 to v2 across four phases |
| `part3_migration_sequence.png` | PNG export of the migration sequence diagram |

## Key Highlights

- **Strict-client assumption applied throughout** — all compatibility analysis assumes clients reject unknown fields and break on renamed keys, surfacing risks that a lenient-client analysis would miss (e.g. Change A flagged as potentially breaking despite being a MINOR semver bump)
- **Semantic vs syntactic breaking changes distinguished** — Change D (title max length 500 → 100) is classified MAJOR despite the JSON field name and type being unchanged, because the contract narrowed and existing valid data becomes un-patchable
- **Single deployment, dual handler architecture** — the coexistence plan avoids a full dual deployment by routing v1/v2 at the gateway to handlers within the same service, with the operational cost of dual handler maintenance explicitly named and mitigated via a hard sunset date

## How to View

1. Open `.drawio` files in [draw.io](https://app.diagrams.net) to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation
4. Run code examples (if included) with Python 3
