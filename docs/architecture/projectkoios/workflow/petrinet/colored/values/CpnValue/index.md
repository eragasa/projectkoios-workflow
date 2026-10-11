# `CpnValue`

## Purpose

One explicitly tagged immutable generic colored-Petri-net value. Parameters ---------- kind Exact enum member selecting the active value representation. value Immutable value matching ``kind``. Numeric strings and Boolean-as-number inputs are rejected. Raises ------ TypeError A field has the wrong semantic type. ValueError An integer is outside signed 64-bit range, a real is nonfinite or overflows binary64, or a string-sequence member is empty. Notes ----- Integer inputs to ``REAL`` are canonicalized to built-in ``float`` and may round to the nearest representable binary64 value. This is a generic finite software representation, not a physical quantity or numerical tolerance.

## Contract role

`CpnValue` is an immutable typed contract value declared by
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
