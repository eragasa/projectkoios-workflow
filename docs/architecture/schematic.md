# Architecture documentation schematic

> **Status: provisional architecture candidate.** The hierarchy below is a
> reviewable decomposition, not an accepted package layout.

## Responsibility

This document explains how the documentation hierarchy maps to a candidate implementation hierarchy and prevents architectural ownership from being flattened into one repository-wide link list.

```text
docs/architecture/
└── projectkoios/                       Python namespace
    └── workflow/                       product package
        ├── sdk/                        external implementation boundary
        ├── compilation/                source-to-CPN compiler and linker
        ├── cpn/                        authoritative process kernel
        ├── registry/                   immutable definitions and capabilities
        ├── runtime/                    occurrences, attempts, and orchestration
        ├── persistence/                durable events and projections
        ├── worker/                     isolated plugin hosting
        ├── service/                    control-plane actions
        ├── api/                        authenticated transport adapter
        └── visualization/              read-only CPN projection
```

At deeper levels, a module directory describes a cohesive candidate implementation concern and a class directory describes one proposed public nominal contract. Cross-links may provide context, but each directory must state its own behavior and exclusions.

Alternative physical packaging remains open: the SDK, service, and worker may be separate distributions from one repository or strict import boundaries within one distribution. Review must choose using dependency, compatibility, deployment, and release evidence rather than treating this tree shape as the decision.
