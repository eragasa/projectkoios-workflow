# `projectkoios.workflow.sdk` implementation

## Responsibility

Build the SDK as a separately installable distribution from `sdk/` in this
repository. The distribution is `projectkoios-workflow-sdk`, its non-overlapping
public import root is `projectkoios.workflow_sdk`, and its first target version
is `0.1.0a1`. The alpha has only Python standard-library runtime dependencies.
The existing `projectkoios-workflow` service distribution depends inward on the
SDK; the SDK never imports service, persistence, compiler, CPN-kernel
implementation, or owner-package modules.

Public records are frozen and slotted, reject unbounded or noncanonical data,
and carry explicit contract versions. Runtime extension boundaries use nominal
ABCs and explicit validation; static generic parameters cannot substitute for
runtime enforcement. ABCs have no hidden discovery or storage behavior.

The first alpha implements exactly the authorized inventory in
[`public_api.md`](public_api.md) and the canonical encodings in
[`serialization.md`](serialization.md), limited to the minimum pure-firing
surface needed for an end-to-end consumer fixture. `Firer.fire()` is a concrete validated
template method; `Firer.__init_subclass__()` rejects subclasses that replace it,
and consumer integrations implement the abstract `_fire()` hook. Prepare,
stage, start, observe, reconcile, cancel, collect, claims, leases, and effect
dispatch remain excluded until their separate architecture gates pass.

Authorized owner refactors in Ingestion, References, Simulations, Applications,
and `ksdft2effmass` are independent work. They should produce runtime-neutral
typed owner actions and evidence under their own accepted contracts, not import
provisional Workflow types. Architecture review should compare those converging
shapes before freezing SDK abstractions. Later compatibility may use direct
implementation, an owner adapter, or a generated/declared descriptor; no
reflective auto-wiring is implied.

Reusable bases may calculate content identities, validate inheritance chains, enforce request/result types, and construct closed outcome records. They must not implement scientific policy, mint authority, launch executables, retry effects, or mutate CPN state.

Any accepted SDK would require contract tests against pinned owner fixtures before owner packages adopt it.
