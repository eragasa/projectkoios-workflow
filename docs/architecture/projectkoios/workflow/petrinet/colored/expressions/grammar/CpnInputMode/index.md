# `CpnInputMode`

## Purpose

Generic input-inscription token behavior. Attributes ---------- CONSUME Matching tokens are consumed by successful firing. READ Matching tokens enable firing but remain in the successor. INHIBIT Firing is enabled only when no matching token is present.

## Contract role

`CpnInputMode` is a closed enumeration declared by
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
