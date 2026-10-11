# `CpnPlaceMarking`

## Purpose

Immutable semantic token multiset at one generic place. Parameters ---------- place_identity Nominal identity of the represented place. tokens Tuple-backed token multiset. Repeated equal anonymous tokens represent multiplicity and are retained. An individually identified token may occur only once at this place. Input order is canonicalized by generic token semantics rather than caller order. Raises ------ TypeError A field has the wrong nominal type or ``tokens`` is mutable. ValueError One individual token identity occurs more than once.

## Contract role

`CpnPlaceMarking` is an immutable typed contract value declared by
`projectkoios.workflow.petrinet.colored.markings`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
