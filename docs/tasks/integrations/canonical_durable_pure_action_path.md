# Canonical durable pure-action path

## Objective

Turn the already demonstrated replayable durable CPN commit orchestration into
the sole supported write direction for experimental pure actions, without
expanding scope into effects or global scheduler replay.

## Why this is current work

The QE vertical slice used
`ExperimentalWorkflowPureActionDurableCpnCommitService` successfully and proved
that compact commit, CPN replay evidence, lifecycle transition, reservation
consumption, and marking advancement can share one atomic boundary. Leaving the
compact-only writer equally available makes the less replayable path too easy to
select and preserves avoidable legacy-partial history.

## Required work

- [ ] Identify every caller of `ExperimentalWorkflowPureActionCommitService` and
  classify it as compatibility evidence, migration evidence, or unsupported new
  writing.
- [ ] Make the durable CPN commit service the documented default for every new
  pure-action commit.
- [ ] Prevent supported orchestration from writing a compact commit without CPN
  replay evidence.
- [ ] Preserve read compatibility for existing compact-only history as
  `LEGACY_PARTIAL` or conflict; do not fabricate missing transcript or lifecycle
  evidence.
- [ ] Keep request/result/evidence payload bodies and private locators outside
  compact Workflow state.
- [ ] Retain exact idempotence, rollback, crash, concurrency, corruption, and
  source/predecessor revalidation behavior.
- [ ] Document the narrow compatibility status of the compact-only writer and
  its removal or internalization condition.

## Validation

- [ ] New supported commits always return durable CPN replay evidence.
- [ ] Repeating the exact durable commit is idempotent.
- [ ] A compact-only historical commit cannot be upgraded by attaching
  post-commit evidence.
- [ ] Precommit failure leaves reservation, compact state, transcript linkage,
  lifecycle, and marking advancement mutually consistent.
- [ ] Compact replay, CPN refiring, lifecycle replay, and safety-state
  reconstruction continue to invoke no owner.

## Exclusions

This task does not promote all `ExperimentalWorkflow*` APIs, complete plan or
profile closure, add effects, replace an owner workflow engine, or implement
global scheduler replay.
