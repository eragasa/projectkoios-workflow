# `CpnTokenPattern`

## Purpose

One input variable and its nonempty admitted color set. Parameters ---------- variable_identity Nominal variable receiving a matched token's value. allowed_color_identities Nonempty unique color set stored in canonical identity order. Raises ------ TypeError A field has the wrong nominal type. ValueError The admitted color set is empty or contains duplicates.

## Contract role

`CpnTokenPattern` is an immutable typed contract value declared by
`projectkoios.workflow.petrinet.colored.expressions.grammar`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
