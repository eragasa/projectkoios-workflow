# `WorkflowValueMappingDescriptor` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/mappings/values.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `owner_identity`, `adapter_identity`, `adapter_version_identity`, `input_record_type_identity`, `output_record_type_identity`, `input_payload_schema_identity`, `input_payload_codec_identity`, `output_payload_schema_identity`, `output_payload_codec_identity`, `correlation_descriptor_identities`, `maximum_input_bytes`, `maximum_output_bytes`, `contract_version`, `identity`. Public behavior: immutable construction and value access.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowValueMappingDescriptor.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
