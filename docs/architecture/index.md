# Architecture documentation

> **Status: provisional architecture candidate.** This uncommitted tree records
> review material, not an accepted implementation plan, public contract,
> migration authorization, release commitment, or compatibility promise.

## Responsibility

This tree records candidate software boundaries for `projectkoios-workflow`. It mirrors the proposed Python ownership path from `projectkoios` through packages, modules, and public classes. A directory is an architectural boundary under review, not an index category: its documents explain what that candidate boundary would own, what it would not own, and how it could collaborate with adjacent boundaries.

Within the current candidate, the authoritative executable process formalism is a compiled, immutable colored Petri net (CPN). DAGs and task lists may be projections, but they do not define execution. That process-model choice reflects the current operator direction; concrete package names, class names, process splits, persistence technology, and migration order remain provisional.

## Decision discipline

Architecture review may accept, replace, combine, defer, or reject any concrete decomposition described below. Documents use direct language to make invariants testable, not to imply that implementation has been authorized. Alternatives, unresolved decisions, sequencing options, and evidence gates must remain visible until a reviewed decision record closes them.

## Documentation contract

Every directory in this tree contains:

- `index.md`: responsibility, owned concepts, and exclusions;
- `schematic.md`: relationships, data flow, and control boundaries;
- `implementation.md`: target package mapping, invariants, maturity, and migration evidence.

Package and module directories use Python names. Public class directories use the exact class name. These documents describe architecture; accepted contracts and source code remain separately authoritative for their respective concerns.
