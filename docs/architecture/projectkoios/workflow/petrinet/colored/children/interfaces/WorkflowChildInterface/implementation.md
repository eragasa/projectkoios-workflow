# `WorkflowChildInterface` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/children/interfaces.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `input_ports`, `terminal_output_ports`, `admitted_terminal_classification_identities`, `terminal_delivery_requirements`, `cancellation_capability`, `reconciliation_capability_identity`, `execution_protocol_requirement_identity`, `protected_effect_capability_identities`, `contract_version`, `identity`. Public behavior: immutable construction and value access.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowChildInterface.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
