# `CpnMarking`

## Purpose

One complete immutable semantic marking for an exact net definition. Parameters ---------- identity Nominal identity of this exact semantic marking. definition_identity Exact generic definition under which the marking is interpreted. places Unique place markings, including empty places when the definition requires them, stored in canonical place-identity order. Raises ------ TypeError A field has the wrong nominal type or ``places`` is mutable. ValueError Place identities are duplicated or one individual token identity occurs in more than one place. Notes ----- Completeness against a definition is cross-object validation and belongs to a later validator. Revision and wire-schema state are deliberately absent.

## Contract role

`CpnMarking` is an immutable typed contract value declared by
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
