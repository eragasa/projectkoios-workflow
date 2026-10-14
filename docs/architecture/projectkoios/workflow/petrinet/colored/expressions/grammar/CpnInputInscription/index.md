# `CpnInputInscription`

## Purpose

Ordered multiset demand for one generic input arc. Parameters ---------- mode Consume, read, or inhibitor behavior. patterns Nonempty ordered pattern demand. Consume/read modes require binding ``CpnTokenPattern`` members. Inhibitor mode requires nonbinding ``CpnInhibitorPattern`` members because successful absence cannot produce a variable value. Order and duplicates are meaningful. Raises ------ TypeError The mode, tuple, or pattern variant has the wrong semantic type. ValueError The pattern tuple is empty.

## Contract role

`CpnInputInscription` is an immutable typed contract value declared by
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
