# Workflow task priorities

## Current direction

The QE saved-state pilot demonstrates that Workflow adds concrete value for
atomic durable pure-action execution and owner-independent replay. It does not
demonstrate that Workflow should replace an owner's smaller domain-specific
workflow architecture.

The current investment rule is therefore:

> Preserve owner-facing domain workflow facades. Apply Workflow selectively to
> pure operations that need cross-repository contracts, authoritative source
> admission, atomic state advancement, and durable replay.

The existing Simulations `PwDftScfWorkflowFacade`, typed actions/events, and
local SNAKES implementation remain the current SCF lifecycle architecture.
Workflow's QE artifact-set path is a bounded outward integration, not a
replacement for registration, submission, completion, or analysis orchestration.

## Now — consolidate demonstrated value

1. Complete the
   [canonical durable pure-action path](integrations/canonical_durable_pure_action_path.md):
   make replayable durable CPN commit the supported write path and constrain the
   compact-only compatibility writer.
2. Preserve the
   [selective Simulations adoption boundary](integrations/simulations/selective_runtime_adoption.md)
   and keep the protected core and reusable owner workflow contracts independent
   of Workflow runtime services.
3. Keep the QE source adapter content-addressed and fail closed on missing,
   incompatible, corrupt, or uncertain source observations.
4. Retain the exact QE vertical-slice evidence and deterministic vectors without
   claiming OS-process isolation, production release readiness, or complete
   CPN-bindings conformance.

Do not add another replay variant, persistence layer, or internal orchestration
record unless one of these tasks exposes a concrete missing safety property.

## Next — test generality before expansion

1. Run the [second owner SDK pilot](integrations/second_owner_pilot.md) as an
   owner-side pure-action test first. Do not require complete Workflow runtime
   promotion merely to learn whether the SDK abstraction generalizes.
2. If the second owner succeeds, close the minimum plan/profile, packaging,
   compatibility, and source-authority guarantees required for a supported pure
   path.
3. Validate real OS-process worker loading and failure isolation before calling
   worker isolation complete.
4. Then activate the
   [experimental surface retirement](tech_debt/retire_experimental_action_surface.md)
   and [broader adoption gate](integrations/broader_adoption_gate.md).

## Later — separately gated capabilities

- Effect dispatch, reconciliation, cancellation, retries, and ambiguous outcomes
  remain behind the [effectful integration gate](integrations/effectful_integration_gate.md).
- A Workflow-backed implementation of an existing owner lifecycle facade may be
  evaluated only after that gate passes and only through owner-controlled
  behavioral equivalence tests.
- Global multi-occurrence scheduler replay and complete CPN-bindings replay are
  deferred until a real owner requires them.

## Explicitly not prioritized

- replacing Simulations' current SCF facade or local SNAKES lifecycle;
- moving owner domain actions, events, codecs, or identities into Workflow;
- making protected owner code import Workflow service, persistence, compiler, or
  CPN runtime implementations;
- effectful execution through the pure `Firer` boundary;
- infrastructure growth justified only by internal architectural completeness;
  or
- claiming full CPN-bindings conformance from bounded experimental records.

## Revisit conditions

Revisit the ordering only when at least one of the following occurs:

- a second owner cannot integrate without a concrete SDK or runtime change;
- a production pure action requires guarantees absent from the durable QE path;
- an owner requests durable effect lifecycle behavior and the effectful gate has
  accepted semantics; or
- operating evidence shows the existing owner architecture cannot satisfy a
  required durability, concurrency, or replay property.
