# Task Board API -- Compatibility and Coupling

## File Map

```
submissions/YOUR_NAME/
├── part1_coupling_analysis.md        7 dependency pairs, coupling facets, 2 tight / 2 reduce
├── part1_coupling_diagram.drawio
├── part1_coupling_diagram.png
├── part2_compatibility_changes.md    Changes A-E: breaking/non-breaking, semver, semantic risk
├── part2_version_coexistence.md      /v1 + /v2 path prefix, gateway routing, sunset timeline
├── part3_compatibility_policy.md     Governance: additive rules, deprecation, error stability, partners
├── part3_migration_sequence.drawio   4-phase: old client, migration, sunset (410), v2 only
├── part3_migration_sequence.png
└── README.md
```

## Key Decisions

- **Breaking changes**: B (field rename), C (required header), D (semantic max-length reduction) are all MAJOR.
- **Non-breaking**: A (optional field, tolerant readers) and E (new endpoint) are MINOR.
- **Coexistence**: path prefix (`/v1`, `/v2`) -- explicit, log-visible, no custom header.
- **v1 sunset**: 12 months for first-party, 18 months for partners; `410 Gone` with migration URL.
- **Error code stability**: `code` values are frozen per major version; `message` strings are not.
