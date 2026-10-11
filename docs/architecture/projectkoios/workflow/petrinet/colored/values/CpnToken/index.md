# `CpnToken`

## Purpose

One color-qualified immutable generic token value. Parameters ---------- color_identity Nominal identity of the token's color. value Generic immutable value carried by the token. token_identity Optional nominal identity used when individual correlation matters. ``None`` denotes an indistinguishable token value whose multiplicity is represented solely by its containing marking. Raises ------ TypeError A field has the wrong nominal type. Notes ----- The token deliberately carries no multiplicity. Equal anonymous tokens are counted by the containing ``CpnMarking``. Individually meaningful simulation attempts and results are not anonymous multiplicities; their Workflow-owned identities remain outside this generic package.

## Contract role

`CpnToken` is an immutable typed contract value declared by
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
