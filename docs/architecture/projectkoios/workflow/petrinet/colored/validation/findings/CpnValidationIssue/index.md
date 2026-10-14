# `CpnValidationIssue`

## Purpose

One immutable structural validation finding. Parameters ---------- code Stable v2 semantic issue code. path Nonempty exact structural path from the validated root. related_identities Nonempty lexical identities stored canonically. Repeated lexical values are retained when distinct nominal identity classes share the same spelling. message Nonempty sanitized diagnostic with no authority or scientific meaning. Raises ------ TypeError A field has the wrong semantic type or a collection is mutable. ValueError A required tuple or string is empty.

## Contract role

`CpnValidationIssue` is a structured validation finding declared by
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
