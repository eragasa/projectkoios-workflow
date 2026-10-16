# Canonical durable pure-action path

## Objective

Turn the already demonstrated replayable durable CPN commit orchestration into
the sole supported write direction for experimental pure actions, without
expanding scope into effects or global scheduler replay.

## Iteration-2 terminology

This completed task retains `pure-action` in filenames, APIs, identities, and
evidence because that is the implemented prerelease vocabulary. Architecture
iteration 2 treats this chain as the candidate executor for one pure atomic
Task. Renaming or promoting it requires an explicit compatibility migration and
must preserve schemas, identities, canonical bytes, and replay behavior.

## Why this was required

The QE vertical slice used
`ExperimentalWorkflowPureActionDurableCpnCommitService` successfully and proved
that compact commit, CPN replay evidence, lifecycle transition, reservation
consumption, and marking advancement can share one atomic boundary. Leaving the
compact-only writer equally available makes the less replayable path too easy to
select and preserves avoidable legacy-partial history.

## Required work

- [x] Identify every caller of `ExperimentalWorkflowPureActionCommitService` and
  classify it as compatibility evidence, migration evidence, or unsupported new
  writing.
- [x] Make the durable CPN commit service the documented default for every new
  pure-action commit.
- [x] Prevent supported production orchestration from writing a compact commit
  without CPN replay evidence. An AST architecture test rejects production
  execution-module calls to the compact-only service.
- [x] Preserve read compatibility for existing compact-only history as
  `LEGACY_PARTIAL` or conflict; do not fabricate missing transcript or lifecycle
  evidence.
- [x] Keep request/result/evidence payload bodies and private locators outside
  compact Workflow state.
- [x] Retain exact idempotence, rollback, crash, concurrency, corruption, and
  source/predecessor revalidation behavior.
- [x] Document the narrow compatibility status of the compact-only writer and
  its removal or internalization condition.

## Caller inventory

Production execution modules contain no call to the compact-only service. Its
public export remains solely as prerelease compatibility surface. Current test
callers are intentionally retained in these categories:

- compact commit construction, atomicity, concurrency, and compact replay
  evidence;
- SQLite v2 legacy-history and migration evidence;
- durable-commit conflict with a pre-existing compact-only commit; and
- `LEGACY_PARTIAL` lifecycle and safety-state reconstruction evidence.

The durable service reuses private compact candidate construction helpers but
never invokes the compact-only service.

## Validation

- [x] New supported commits use the durable service and return durable CPN replay
  evidence.
- [x] Repeating the exact durable commit is idempotent.
- [x] A compact-only historical commit cannot be upgraded by attaching
  post-commit evidence.
- [x] Precommit failure leaves reservation, compact state, transcript linkage,
  lifecycle, and marking advancement mutually consistent.
- [x] Compact replay, CPN refiring, lifecycle replay, and safety-state
  reconstruction continue to invoke no owner.

## Completion evidence

- `tests/projectkoios/workflow/runtime/test__CanonicalDurablePureActionCommitPath.py`
  enforces the production-caller boundary while retaining the compatibility
  export.
- Existing durable commit, persistence, replay, lifecycle, safety-state,
  corruption, concurrency, rollback, and crash tests remain authoritative for
  behavior.
- The QE real-owner vertical slice uses only the durable service.

## Exclusions

This task does not promote all `ExperimentalWorkflow*` APIs, complete plan or
profile closure, add effects, replace an owner workflow engine, or implement
global scheduler replay.
