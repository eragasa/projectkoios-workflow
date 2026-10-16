# `projectkoios.workflow.sdk` implementation

## Responsibility

Build the SDK as a separately installable standard-library-only distribution
from `sdk/`. The service distribution depends inward on the SDK; the SDK never
imports service, persistence, compiler, CPN implementation, or owner packages.

The implemented `0.1.0a1` surface is deliberately narrow. `Firer.fire()` is a
concrete non-overridable validating template method, and consumer integrations
implement `_fire()`. It represents one pure atomic Task invocation but does not
currently expose public `Task` or `Workflow` source classes. Prepare, stage,
start, observe, reconcile, cancel, collect, claims, leases, effects, and child
runs remain excluded.

Architecture iteration 2 may add nominal source ABCs only after two owner shapes
converge. The expected semantic relation is `Workflow(Task)`, with final
immutable-definition construction and no runtime behavior in the source owner.
Task execution remains separate through `Firer`, effect lifecycle handlers, or a
child-run service. Exact API names, fields, generics, serialization, and version
remain undecided.

Public records are frozen and slotted, reject unbounded or noncanonical data,
and carry explicit contract versions. Nominal ABCs enforce runtime membership;
static generic parameters cannot replace validation. ABCs have no hidden
discovery, storage, authority, or execution behavior.

Owner adoption should begin through outward adapters. Simulations must retain
its calculator-neutral SCF lifecycle and QE/VASP Task records. Numerical
experiments must retain typed Definition-to-Result APIs and owner-controlled
arrays/evidence. Direct inheritance from future SDK source ABCs is considered
only after adapter parity and dependency tests pass.

Reusable bases may calculate content identities, validate inheritance, enforce
request/result types, and construct closed outcomes. They must not implement
scientific policy, mint authority, launch executables, retry effects, create
child runs, or mutate CPN state.
