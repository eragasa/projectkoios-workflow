# `WorkflowExecutionPlanClosure` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/plans/definition.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `nominal_definition_identity`, `canonical_definition`, `cpn_execution_profile_identity`, `initial_marking_contract_identity`, `payload_color_bindings`, `transition_routes`, `child_bindings`, `child_interface`, `terminal_delivery_requirements`, `owner_mapping_descriptors`, `compiler_identity`, `compiler_version`, `contract_version`. Public behavior: `canonical_definition_identity()`, `canonical_definition_representation_profile_identity()`, `canonical_definition_sha256()`.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowExecutionPlanClosure.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
