# `WorkflowChildDefinitionExportClosure` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/children/exports/definition.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `owner_identity`, `workflow_family_identity`, `source_definition_identity`, `source_definition_contract_version`, `execution_plan_identity`, `execution_plan_sha256`, `nominal_definition_identity`, `canonical_definition_identity`, `canonical_definition_representation_profile_identity`, `canonical_definition_sha256`, `cpn_execution_profile_identity`, `initial_marking_constructor_identity`, `interface`, `compiler_implementation_identity`, `compiler_version_identity`, `exporter_implementation_identity`, `exporter_version_identity`, `source_revision_identity`, `contract_version`. Public behavior: immutable construction and value access.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowChildDefinitionExportClosure.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
