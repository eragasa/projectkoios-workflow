# WF-ISSUE-0018 — Provisional ksdft2effmass workflow-v2 migration debt

- **Kind:** dependency
- **Status:** BLOCKED_BY_DEPENDENCY
- **Workflow-local scope:** eventual generic contract crosswalk and owner migration
- **Authoritative owner:** `ksdft2effmass` until an accepted Project Koios Workflow contract exists

## Problem or question

How will the provisional `ksdft2effmass.workflows.v2` implementation be crosswalked and migrated into the eventual authoritative Project Koios Workflow distribution without silently changing identities, serialization, failure, replay, or consumer behavior?

## Current evidence

The operator selected Project Koios Workflow as the eventual generic owner. Until that distribution exists, provisional implementation lives in the silicon worktree at `python/src/ksdft2effmass/workflows/v2/`. Shared thin DataObject, Request, Actionizer, and Result bases live separately at `python/src/ksdft2effmass/base/`. Existing `ksdft2effmass.workflows` v1 remains unchanged and there is no compatibility alias.

The owner records migration debt at `/Users/eugene/worktrees/ksdft2effmass-silicon-wannier-kinetic-prototype/docs/tech_debt/workflow-v2-projectkoios-migration/index.md`. The record covers approximately 9.1k lines of provisional duplication, an exact future class/identity/serialization/failure/replay crosswalk, delayed large-module decomposition, narrowing `_LocalWorkflowRuntime` inheritance, consumer migration, and eventual separately authorized removal without aliases.

Owner validation reports Ruff and format passing; strict mypy over 426 source files; 87 focused base/v2 tests; a broader suite of 4,801 passed and 3 skipped excluding an existing pip-dependent wheel module; strict Sphinx; and uv source/wheel builds with isolated wheel import. No QE/Wannier90 execution, dependency change, commit, or push occurred. These results validate the provisional owner slice, not an accepted Workflow contract or cross-repository equivalence.

## Consequence

Treating v2 as the authoritative target would prematurely freeze owner-local duplication. Ignoring it would lose substantial tested compiler/runtime evidence and make later migration unverifiable. Aliasing v1, v2, and Project Koios identities could hide semantic divergence.

## Alternatives and recommendation

Retain v2 as owner-local provisional evidence with no dependency on an unaccepted Workflow SDK. Once Workflow contracts stabilize, construct an explicit bidirectional crosswalk for every public class and identity, canonical serialization, closed failure, replay behavior, and retained fixture. Decompose large modules only where the accepted ownership boundaries require it. Migrate consumers deliberately and add no silent alias.

## Resolution gate

An accepted Workflow contract and provenance-bound migration plan demonstrate exact crosswalk/equivalence, classify intentional differences, pass retained owner fixtures through the authoritative compiler/runtime, inventory and migrate every consumer, narrow or replace local runtime inheritance, and obtain separate authorization before removing provisional code. V1 remains unchanged until its own independent migration gates are met.

## Affected architecture

Base-contract packaging in [`WF-ISSUE-0001`](WF-ISSUE-0001.md), SDK/wire compatibility in [`WF-ISSUE-0006`](WF-ISSUE-0006.md), compiler/plan/linker migration, replay, provenance, and architecture-acceptance evidence in [`WF-ISSUE-0013`](WF-ISSUE-0013.md).
