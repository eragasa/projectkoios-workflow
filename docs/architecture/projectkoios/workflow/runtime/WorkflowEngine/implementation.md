# `WorkflowEngine` implementation

## Responsibility

Adapt the invocation invariants of historical `workflows/engine.py`, blob
`cd39ac8e9684ff08ba012d8dda50bc089293969f`, while generalizing beyond
synchronous in-process execution.

The engine accepts the exact binding aggregate produced by the linker. For one
pure external action it must:

1. load the exact predecessor marking, selected binding, reservation,
   transition-firer binding, and result-mapping descriptor;
2. re-resolve authoritative inputs, revalidate the predecessor, and validate the
   live nominal worker integration against the retained SDK manifest;
3. invoke the exact SDK firer, contain provider exceptions, canonically admit a
   closed correlated result, and revalidate inputs and predecessor again;
4. invoke the mapping only for a current success and validate its candidate
   external variable against the compiled transition;
5. revalidate the reservation immediately before firing;
6. call `ColoredPetriNetTransitionFirer` only for admitted success; and
7. atomically retain SDK request/result/evidence, mapping identity, external
   binding, firing audit, successor marking, and occurrence history.

For a canonical ASCII logical-identity output, admission rejects whitespace,
controls, non-ASCII data, machine paths, trailing bytes, an incompatible CPN
value kind, and any attempt to use an evidence payload digest as the owner
identity. Workflow treats the accepted string as opaque and imports no owner
class or codec implementation.

Replay rehydrates the retained records and never reinvokes the owner firer or
recomputes an identity to repair missing evidence. Pure actions, external
effects, and nested routes retain distinct lifecycles. Uncaught provider
exceptions are contained by the worker boundary; rejected, failed, ambiguous,
or stale outcomes never reach pure CPN firing.

## Experimental predecessor-reservation candidate

`ExperimentalWorkflowPureActionReservationService` is a bounded candidate for
the pre-invocation and post-invocation current-state checks. It accepts only an
exact reconstructed, repository-authorized input aggregate rather than
independently supplied raw inputs. Immediately before reservation it reloads
each opaque source reference and compares its source-owner revision, evidence,
and exact payload. It content-identifies the current v0 reservation shape over
the plan, deployment binding, selection evidence, input admission, source
authorization, request, predecessor marking/revision, occurrence, and attempt.
Earlier v0 experimental reservation shapes remain reconstructable. A nominal
repository ABC owns atomic predecessor reserve and revalidate operations.

The included in-memory repository is thread-safe, non-durable software evidence.
It admits at most one distinct reservation per net-instance predecessor, treats
an exact replay as idempotent, and rejects stale, conflicting, absent, or known
consumed reservations. Its whole-predecessor lock granularity is deliberately
conservative. A separate nominal source-repository ABC preserves owner storage
ownership and closed uncertainty outcomes; Workflow retains only bounded
references and content identities. A production owner adapter, CPN firing,
atomic reservation consumption, successor persistence, and replay remain outside
this candidate. In particular, the candidate exposes no standalone consume
operation: reservation consumption must later share the accepted atomic boundary
with CPN firing and persistence.

## Experimental owner-invocation candidate

`ExperimentalWorkflowPureActionInvocationService` bounds the next phase. It
accepts only the exact repository-authorized aggregate and successful
reservation result. Before invoking an owner it reloads all source observations,
revalidates the predecessor, validates the nominal worker integration against
its retained manifest, resolves the exact request-selected firer, and repeats
both current-state checks after that live integration lookup.

The service invokes the SDK's concrete `Firer.fire()` boundary, canonically
round-trips the closed result, contains worker and provider exceptions, and
repeats source and predecessor revalidation after every owner call, including a
call that raises. The owner receives a separate canonical request copy, and an
attempt to mutate it is contained as an invocation error. Owner rejection,
owner failure, pre-invocation staleness,
post-invocation staleness, worker rejection, invocation error, mapping rejection,
and current mapped success remain distinct content-identified outcomes. Only a
current SDK success reaches the exact plan-selected output mapper.

This v0 invocation candidate produces a candidate external CPN binding only. It
does not claim invocation durability or exactly-once dispatch. The compiled
transition is still supplied to the service and must be closed authoritatively
by the eventual complete execution plan.

## Experimental pure-CPN-firing candidate

`ExperimentalWorkflowPureActionFiringService` correlates a mapped invocation
outcome with the exact authorized inputs, active reservation, selected-binding
evidence, supplied flat definition, and supplied predecessor marking. It repeats
source and predecessor revalidation before constructing
`ColoredPetriNetFiringInput`, invokes the provenance-bound pure
`ColoredPetriNetTransitionFirer`, and revalidates again after computation.

The CPN firer remains authoritative for definition and marking validation,
enablement and selection replay, external-output assignment and color
validation, token-occurrence reconstruction, output evaluation, audit, and
successor derivation. A CPN rejection, unexpected firing exception,
pre-computation stale state, post-computation stale state, and current candidate
success remain distinct outcomes. Direct outcome reconstruction replays the pure
firing and requires an exact result.

This candidate does not consume the reservation or advance an authoritative
marking. A bounded CPN plan extension now binds canonical flat-definition bytes,
their profile and digest, and an exact candidate execution-profile identity; the
reservation binds that CPN-plan identity and firing verifies the supplied
definition byte-for-byte. The candidate profile still omits several
representations and semantic sections required by the complete umbrella
contract, and the predecessor marking remains a correlated runtime argument.
Durable persistence, committed replay, and complete plan closure remain future
work.

## Experimental atomic-commit candidate

`ExperimentalWorkflowPureActionCommitService` constructs one compact,
content-identified commit from the exact CPN plan, repository-authorized source
observations, reservation, mapped owner result, pure CPN firing result, and
predecessor/successor marking coordinates. It retains identities only and does
not move inline owner payload bodies or private locators into commit state.

The nominal reservation repository owns one atomic `commit` operation. The
in-memory reference implementation uses the reservation lock to verify the
active current predecessor, retain the commit identity and marking coordinates,
consume the reservation, and advance the current marking revision together.
Exact replay is idempotent, a distinct commit conflicts, and stale state cannot
commit. State is prepared on copies and swapped only at the final commit point,
so a pre-swap exception leaves repository state unchanged. No standalone consume
operation exists.

A purpose-built experimental SQLite repository now persists the complete compact
commit record, ordered source-authority reference/revision/evidence identities,
reservation consumption, and successor coordinate under one transaction. It
supports exact replay idempotence, reopen reconstruction, concurrent
single-winner commit, injected precommit rollback, and recovery from a separate
process exiting with an uncommitted marking update. Owner payload bodies and
private locators do not enter its schema.

A strict canonical JSON codec now retains exact identity-only committed-event
bytes, including net instance, beside the typed compact columns. One closed
snapshot read returns coordinates, record, and exact bytes atomically while
preserving absent, incompatible, corrupt, and error outcomes. A read-only replay
service verifies the snapshot, reconstructs the compact commit and full
coordinates, and does not call an owner firer, source repository, owner codec,
or CPN firer. This remains bounded structural replay only.

A separate in-memory `ExperimentalWorkflowPureActionCpnReplayBundle` now binds
one exact candidate CPN plan and retained execution profile to canonical
definition, predecessor-marking, and successor-marking bytes, selected and
external-output bindings, directed-selection identity or absence, and the
expected firing-result identity. Its strict canonical codec verifies the
complete candidate plan identity and exact bytes. The pure replay service
rebuilds enablement and selection, invokes only
`ColoredPetriNetTransitionFirer`, and compares the complete result identity and
successor. Unsupported but internally consistent retained profiles remain
`INCOMPATIBLE`; transcript corruption remains distinct from unexpected replay
errors.

Replay-bundle records and construction, canonical transcript serialization,
evidence records/factory, the nominal durable repository port, and pure/durable
refiring orchestration are implemented in separate execution modules. Runtime
reservation records, the nominal repository port, in-memory implementation, and
service orchestration are likewise separated behind their existing compatibility
exports. The public experimental imports and canonical bytes remain unchanged.

The SQLite format-version-3 candidate durably retains the canonical transcript
in a content-addressed table and links it to the compact commit in the same
reservation-consuming transaction. Its nominal evidence port admits only a
bundle already correlated with the compact commit. The dedicated durable CPN
commit service constructs that bundle internally from the reconstructed plan
and successful CPN firing result, requires the reservation service and evidence
port to own the same repository instance, revalidates source observations, and
then calls the single atomic operation. It exposes no caller-supplied transcript
parameter and cannot attach evidence after an earlier compact-only commit.
Atomic reads verify bundle
and association digests and recheck plan, firing-result, predecessor, and
successor identities against the compact row before pure refiring. Legacy
version-2 commits migrate without fabricated links and return a closed absent
evidence outcome. Definitions and marking bodies remain absent from the compact
commit event itself.

Complete request/result history, reservation lifecycle, runtime safety-state
reconstruction, and complete CPN-bindings replay remain unimplemented.

Source resolution and predecessor commit also remain sequential across nominal
repositories rather than one distributed transaction; production source
revision immutability must close that remaining observation race.

## Internal validation ownership

The execution package's private `_validation` module owns reconstruction of
repository-authorized inputs, successful-reservation correlation, canonical SDK
request cloning at execution trust boundaries, and CPN-plan reconstruction.
Invocation and firing outcome reconstruction remain with their defining phase
modules. Invocation, firing, and commit reuse these helpers; they do not carry
phase-local copies of the same reservation and plan checks. This organization
changes neither identity preimages nor public experimental records.
