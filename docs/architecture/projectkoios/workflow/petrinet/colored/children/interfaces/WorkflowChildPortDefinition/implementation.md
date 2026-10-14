# `WorkflowChildPortDefinition` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/children/interfaces.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `identity`, `direction`, `place_identity`, `color_identity`, `payload_schema_identity`, `payload_codec_identity`, `scalar_value_kind`, `minimum_token_count`, `maximum_token_count`, `correlation_descriptor_identities`, `traffic_kind`, `contract_version`. Public behavior: immutable construction and value access.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowChildPortDefinition.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
