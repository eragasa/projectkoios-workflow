# `CpnBinding`

## Purpose

One immutable ordered variable/value binding for a transition. Parameters ---------- transition_identity Nominal identity of the transition for which values are bound. assignments Complete variable/value assignments in the owning definition's declared variable order. This DataObject preserves that order and requires unique variable identities; it does not infer or lexically reorder policy. Raises ------ TypeError A field has the wrong nominal type or ``assignments`` is mutable. ValueError A variable identity occurs more than once.

## Contract role

`CpnBinding` is an immutable typed contract value declared by
`projectkoios.workflow.petrinet.colored.bindings`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
