# `WorkflowCpnExecutionProfile` implementation

## Source mapping

The class is defined in `src/python/projectkoios/workflow/petrinet/colored/profiles/definition.py` as an immutable typed contract value. Explicit bases: no explicit base class.
Declared fields: `value_model_identity`, `expression_grammar_identity`, `canonical_json_parser_identity`, `canonical_definition_codec_identity`, `canonical_control_record_codec_identity`, `canonical_marking_representation_identity`, `canonical_binding_representation_identity`, `canonical_directive_representation_identity`, `canonical_enablement_result_representation_identity`, `canonical_selection_result_representation_identity`, `canonical_firing_result_representation_identity`, `definition_validator_identity`, `marking_validator_identity`, `control_record_type_graph_validator_identity`, `control_record_schema_validator_identity`, `expression_structure_validator_identity`, `expression_bounds_validator_identity`, `field_projector_identity`, `control_record_constructor_identity`, `expression_evaluator_identity`, `guard_evaluator_identity`, `value_canonicalizer_identity`, `value_canonical_decoder_identity`, `value_expression_canonicalizer_identity`, `value_expression_decoder_identity`, `guard_canonicalizer_identity`, `guard_decoder_identity`, `expression_variable_collector_identity`, `guard_expression_collector_identity`, `guard_variable_collector_identity`, `value_ordering_policy_identity`, `token_ordering_policy_identity`, `external_output_validator_identity`, `input_arc_validator_identity`, `output_arc_validator_identity`, `complete_enabler_identity`, `enablement_failure_builder_identity`, `enabled_binding_ordering_identity`, `binding_selector_identity`, `transition_firer_identity`, `token_occurrence_reconstructor_identity`, `firing_result_identity_deriver_identity`, `successor_marking_builder_identity`, `firing_failure_builder_identity`, `shadow_firer_identity`, `shadow_firing_replayer_identity`, `execution_plan_compiler_identity`, `child_definition_exporter_identity`, `execution_profile_resolver_identity`, `semantic_version`. Public behavior: immutable construction and value access.

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

The dedicated class test is `tests/projectkoios/workflow/petrinet/colored/test__WorkflowCpnExecutionProfile.py`. Package-wide gates additionally check strict typing, Ruff, full
pytest, public nominality, exact provenance, acyclic package imports, and built
artifacts. Passing those gates establishes software verification only.
