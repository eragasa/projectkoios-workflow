# `CpnShadowFiringResult` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/shadow/contracts.py` as an immutable operation result. Explicit bases: no explicit base class.
Declared fields: `identity`, `canonical_definition_identity`, `canonical_definition_sha256`, `execution_profile_identity`, `predecessor_marking_identity`, `predecessor_marking_sha256`, `firing_result_identity`, `successor_marking_identity`, `successor_marking_sha256`, `firing_result`. Public behavior: immutable construction and value access.

## Invariants and failures

Construction and public methods enforce the exact source checks. Bounded parsing,
canonicalization, validation, mapping, linking, selection, and firing remain
separate concerns. The class must not broaden admitted values through subclass
coercion, executable source, dynamic imports, or ambient services.

## Composition strategy

Use already typed collaborators and retain returned identities or findings for
correlation. Operation identities belong in the applicable execution profile;
content identities derive from complete semantic state. Child-plan reference
cycle checks apply only to static plan containment, never CPN topology.

## Verification

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__CpnShadowFiringResult.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
