# Review Principles

## Architecture principles

### AP-001: Preserve the core boundary

Core schema/model code must not depend on UI, runtime engines, Petri-net libraries, process-mining libraries, or external adapters.

Good:

schema <- runtime
schema <- ui
schema <- petri
schema <- adapters

Bad:

schema -> runtime
schema -> ui
schema -> snakes
schema -> pm4py

### AP-002: Separate objects from actions

Objects carry state.

Actions transform state.

`ObjectClass` defines artifact/token types.

`ActionClass` defines transition/action types.

Object classes should not execute actions.

Action classes should not own persistent object state.

### AP-003: Keep Petri-net compatibility possible

The workflow model should be expressible as places, transitions, markings, guards, and firing events.

The core model should not directly depend on a Petri-net library.

### AP-004: Dry-run before mutation

Any mutating action should have a dry-run path that reports the expected state change before execution.

### AP-005: Provenance is required

Any meaningful state transition should produce a provenance record.

### AP-006: Prefer small current abstractions

Do not add abstractions for speculative future needs.

A new abstraction is justified only if it protects a current boundary, removes real duplication, isolates an unstable dependency, or represents a real domain concept.

## Code principles

### CP-001: Public API first

Tests should primarily exercise public behavior.

### CP-002: Explicit mutation

Mutating functions should be named and typed clearly.

Good:

`dry_run()`

`fire()`

`commit()`

Bad:

`process()`

`resolve()`

`update_everything()`

### CP-003: Thin adapters

External libraries belong behind adapters.

### CP-004: Test invariants

Tests should check important invariants:

- dry-run does not mutate state
- disabled actions cannot fire
- core does not import UI
- core does not import Petri-net backends
- successful action produces provenance
