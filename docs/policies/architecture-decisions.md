# Workflow architecture decisions

This document owns the rationale for Workflow package boundaries. The normative,
human-authored machine-readable dependency and effect policy is
[`workflow-architecture-policy.json`](workflow-architecture-policy.json). The
source-derived observations are generated separately in
[`architecture-baseline.md`](architecture-baseline.md). Neither generator nor
its output may introduce or silently revise architecture policy.

## Semantic operation ownership

One independently callable semantic action belongs to one module. The module
may also own that action's immutable request, response, findings, and identity.
This keeps replacement, review, versioning, and dependency analysis aligned
with an executable semantic unit rather than a broad topic bucket.

A canonical codec is the sole exception: one codec class may expose its paired,
typed `encode` and `decode` methods because those methods jointly define one
wire representation. Two classes exposing `execute` are two actions and must
have separate owner modules. Each action or codec exposes no other public
callable operation, and every retained semantic identity resolves to exactly one
module/class owner across the complete SDK.

## Namespace boundaries

Package initializers contain only a docstring and an explicit empty `__all__`.
They identify namespaces; they do not aggregate, re-export, register, or discover
implementations. Consumers import directly from the semantic owner recorded in
the checked SDK manifest.

Compound concepts use nested noun namespaces rather than compound package or
module names. This rule is structural, not an instruction to create depth
without ownership: a new namespace must identify a durable semantic owner.

## Dependency direction

Workflow uses the layer matrix explicitly approved in the human-authored
`workflow-architecture-policy.json`. Core remains engine-neutral. Persistence
owns opaque revision mechanics. Runtime
coordinates core transitions through persistence interfaces without importing
CPN implementations. Review workflows depend on core contracts. The CPN SDK is
self-contained and does not import runtime, persistence, review, providers, or
scientific repositories.

All production imports participate in one alias-aware, repository-wide graph.
Dynamic imports are prohibited because they would make review and cycle checks
incomplete.

## Composition roots

High fan-out is permitted only at named composition roots. A composition root
must explicitly assemble independently owned operations; it must not hide
provider lookup, runtime discovery, callbacks, or a service locator.

`petrinet.colored.profiles.building` is the current composition root. Its exact
intended dependency set is normative policy, not a generated fanout threshold.
The broad dependency set is intentional because the resulting profile closes
over every supported CPN component identity. Formatting imports onto fewer
lines does not reduce or conceal that coupling. Adding, removing, or substituting
an edge requires an explicit human-authored policy change.

## Runtime effects

The runtime package is an effect-free coordinator. It may depend on immutable
core contracts, runtime-owned records, and opaque persistence interfaces.
Network access, subprocess execution, ambient time, randomness, provider code,
and CPN engines require separately owned ports and adapters and cannot be
imported directly by runtime modules. Runtime therefore uses an exact positive
import policy: every allowed internal port and external standard-library module
is named per runtime module. Any new module or import requires an explicit policy
change, regardless of the dependency's package spelling.

Architecture tests recursively scan the complete source package and require the
observed runtime module set and every internal and external import set to equal
the human-authored policy. A test that scans no substantive module is a failed
architecture test, not passing evidence.

## SDK stability

Importability does not imply compatibility. The offline SDK manifest records an
audience and stability classification for every discovered public CPN type and
operation. The package remains release-candidate-only until a provider-owned
artifact passes conformance and the demonstrated provider surface is selected
for stability.

Stable consumers continue to import semantic owners directly; Workflow does not
create aggregate facade modules or compatibility shims to simulate stability.
