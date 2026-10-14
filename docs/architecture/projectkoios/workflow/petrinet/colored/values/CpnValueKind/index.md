# `CpnValueKind`

## Purpose

Closed tags for generic colored-Petri-net scalar values. Attributes ---------- NONE The sole admitted value is ``None``. BOOLEAN The admitted value is an exact built-in Boolean. INTEGER The admitted value is a signed 64-bit built-in integer. REAL The admitted input is an exact built-in integer or finite float and is stored as finite IEEE-754 binary64. STRING The admitted value is an exact built-in string. STRING_SEQUENCE The admitted value is an ordered tuple of nonempty built-in strings; duplicates are meaningful and preserved.

## Contract role

`CpnValueKind` is a closed enumeration declared by
`projectkoios.workflow.petrinet.colored.values`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
