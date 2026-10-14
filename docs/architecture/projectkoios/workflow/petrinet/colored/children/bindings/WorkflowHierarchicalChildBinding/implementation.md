# `WorkflowHierarchicalChildBinding` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/children/bindings.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `parent_definition_identity`, `transition_route`, `child_export_identity`, `child_execution_plan_identity`, `input_mapping`, `terminal_mappings`, `child_instance_cardinality`, `child_ordinal`, `cancellation_propagation_policy_identity`, `quiescence_required`, `maximum_correlation_field_count`, `maximum_external_output_reference_count`, `contract_version`, `identity`. Public behavior: immutable construction and value access.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowHierarchicalChildBinding.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
