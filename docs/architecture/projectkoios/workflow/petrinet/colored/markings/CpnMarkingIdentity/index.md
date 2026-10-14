# `CpnMarkingIdentity`

## Purpose

Nominal identity of one exact semantic generic marking. Parameters ---------- value Nonempty owner-local lexical identity. This in-memory contract does not select a digest, canonical wire, or revision scheme. Raises ------ TypeError ``value`` is not an exact built-in string. ValueError ``value`` is empty.

## Contract role

`CpnMarkingIdentity` is a nominal or content identity value declared by
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
