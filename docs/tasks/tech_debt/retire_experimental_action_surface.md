# Retire the experimental pure-action surface

## Problem

`ExperimentalWorkflow*` records and services make the current candidate status
visible, but leaving them as a permanent parallel API would preserve ambiguous
ownership, broad `actions` naming, and publicly constructible records that a
future caller could mistake for runtime admission evidence.

## Activation condition

Do not activate this cleanup before the second-owner pilot establishes which
abstractions genuinely generalize. Complete it after that result and before
broader SDK adoption or before declaring the pure external-firing path
supported, whichever occurs first.

## Action

- [ ] Inventory every exported `ExperimentalWorkflow*` symbol and its consumers.
- [ ] Promote, replace, or delete each symbol after the corresponding contract and
  runtime stage is accepted.
- [ ] Place Workflow-owned integration admission under a namespace distinct from
  the standalone owner-facing SDK and the CPN kernel.
- [ ] Ensure candidate and mapped records cannot be mistaken for admitted or
  committed runtime records.
- [ ] Remove compatibility exports only through an explicit recorded migration.
- [ ] Add dependency-direction tests for the final package boundaries.

## Completion evidence

- [ ] Retain a symbol-by-symbol disposition table.
- [ ] Prove supported imports contain no experimental service-side dependency.
- [ ] Retain migration and replay evidence for any renamed retained record.
- [ ] Retain isolated SDK, Workflow, and owner-fixture test results.

This task does not promote an experimental contract solely by removing its
prefix. Promotion requires accepted semantics and complete runtime evidence.
