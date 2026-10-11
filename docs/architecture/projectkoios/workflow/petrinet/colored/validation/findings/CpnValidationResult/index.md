# `CpnValidationResult`

## Purpose

Canonical immutable structural findings from one validation operation. Parameters ---------- issues Complete findings canonicalized by path, code, related identities, and message. Repeated exact findings are retained when repeated malformed occurrences produce them. Raises ------ TypeError ``issues`` is mutable or contains a wrong semantic type.

## Contract role

`CpnValidationResult` is an immutable operation result declared by
`projectkoios.workflow.petrinet.colored.validation.findings`. Its owner is the
source module, not this documentation or a consuming domain repository.

## Composition boundary

The class composes only declared typed values and operations. It has no implicit
provider, callback, resolver, store, filesystem, network, or scientific-policy
access. Successful use does not grant execution or acceptance authority.

## Composition strategy

Construct the exact type, preserve its derived identities, and pass it only to
operations that declare it in their typed boundary. Do not replace it with an
arbitrary object projector, executable expression, import path, or caller label.
