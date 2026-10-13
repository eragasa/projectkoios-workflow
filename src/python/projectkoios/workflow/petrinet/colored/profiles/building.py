"""Reviewed local CPN execution-profile construction and resolution."""

from dataclasses import dataclass
from typing import final

from .. import markings, selection, values
from ..canonical import bindings as canonical_bindings
from ..canonical import definitions as canonical_definitions
from ..canonical import directives as canonical_directives
from ..canonical import enablement as canonical_enablement
from ..canonical import json as canonical_json
from ..canonical import markings as canonical_markings
from ..canonical import selections as canonical_selections
from ..canonical.expressions.guards import canonicalization as canonical_guards
from ..canonical.expressions.guards import decoding as canonical_guard_decoding
from ..canonical.expressions.values import canonicalization as canonical_values
from ..canonical.expressions.values import decoding as canonical_value_decoding
from ..canonical.firing.results import identity as canonical_firing_identity
from ..children.exports.canonical import exporting as child_export_canonical
from ..control.records import canonical as record_canonical
from ..control.records import ordering as record_ordering
from ..control.records import schema as record_schema
from ..control.records.types import graph as record_type_graph
from ..control.records.values import canonicalization as value_canonicalization
from ..control.records.values import decoding as value_decoding
from ..enablement import ordering as enablement_ordering
from ..enablement import transitions as enablement_transitions
from ..enablement.failures import building as enablement_failure_building
from ..expressions.collection import expressions as expression_collection
from ..expressions.collection import guards as guard_expression_collection
from ..expressions.collection import variables as guard_variable_collection
from ..expressions import construction as expression_construction
from ..expressions.evaluation import expressions as expression_evaluation
from ..expressions.evaluation import guards as guard_evaluation
from ..expressions import grammar as expression_grammar
from ..expressions import projection as expression_projection
from ..expressions.validation import bounds as expression_bounds
from ..expressions.validation import structure as expression_structure
from ..firing import transitions as firing_transitions
from ..firing.failures import building as firing_failure_building
from ..firing.markings import successor as firing_successor
from ..firing.occurrences import reconstruction as occurrence_reconstruction
from ..firing.results import identity as firing_identity
from ..outputs import external as external_outputs
from ..plans import compilation as plan_compilation
from ..shadow import contracts as shadow_contracts
from ..shadow.replay import contracts as shadow_replay_contracts
from ..validation.definitions import complete as definition_validation
from ..validation.definitions import input as input_validation
from ..validation.definitions import output as output_validation
from ..validation import markings as marking_validation
from .definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileResolverIdentity,
)


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileBuildingRequest:
    """Explicit immutable request for the reviewed local execution profile."""


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileBuilderIdentity:
    """Identity of exact owner default-profile construction semantics."""

    value: str = "projectkoios.workflow.cpn.execution-profile-builder:0.1"


@final
class WorkflowCpnExecutionProfileBuilder:
    """Directly construct the complete reviewed default CPN operation profile."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowCpnExecutionProfileBuilderIdentity:
        """Return exact profile-construction semantics identity."""
        return WorkflowCpnExecutionProfileBuilderIdentity()

    def execute(
        self, request: WorkflowCpnExecutionProfileBuildingRequest
    ) -> WorkflowCpnExecutionProfile:
        """Return every independently callable component identity explicitly."""
        if type(request) is not WorkflowCpnExecutionProfileBuildingRequest:
            raise TypeError(
                "request must be WorkflowCpnExecutionProfileBuildingRequest"
            )
        return WorkflowCpnExecutionProfile(
            value_model_identity=values.CpnValueModelIdentity().value,
            expression_grammar_identity=expression_grammar.CpnExpressionGrammarIdentity().value,
            canonical_json_parser_identity=canonical_json.CpnCanonicalJsonParserIdentity().value,
            canonical_definition_codec_identity=(
                canonical_definitions.CpnCanonicalDefinitionCodecIdentity().value
            ),
            canonical_control_record_codec_identity=(
                record_canonical.CpnControlRecordCanonicalCodecIdentity().value
            ),
            canonical_marking_representation_identity=(
                canonical_markings.CpnCanonicalMarkingCodecIdentity().value
            ),
            canonical_binding_representation_identity=(
                canonical_bindings.CpnCanonicalBindingCodecIdentity().value
            ),
            canonical_directive_representation_identity=(
                canonical_directives.CpnCanonicalSelectionDirectiveCodecIdentity().value
            ),
            canonical_enablement_result_representation_identity=(
                canonical_enablement.CpnCanonicalEnablementResultCodecIdentity().value
            ),
            canonical_selection_result_representation_identity=(
                canonical_selections.CpnCanonicalSelectionResultCodecIdentity().value
            ),
            canonical_firing_result_representation_identity=(
                canonical_firing_identity.CpnCanonicalFiringResultCodecIdentity().value
            ),
            definition_validator_identity=definition_validation.CpnDefinitionValidatorIdentity().value,
            marking_validator_identity=marking_validation.CpnMarkingValidatorIdentity().value,
            control_record_type_graph_validator_identity=(
                record_type_graph.CpnControlRecordTypeGraphValidatorIdentity().value
            ),
            control_record_schema_validator_identity=(
                record_schema.CpnControlRecordSchemaValidatorIdentity().value
            ),
            expression_structure_validator_identity=(
                expression_structure.CpnExpressionStructureValidatorIdentity().value
            ),
            expression_bounds_validator_identity=(
                expression_bounds.CpnExpressionBoundsValidatorIdentity().value
            ),
            field_projector_identity=expression_projection.CpnFieldProjectorIdentity().value,
            control_record_constructor_identity=(
                expression_construction.CpnControlRecordConstructorIdentity().value
            ),
            expression_evaluator_identity=expression_evaluation.CpnExpressionEvaluatorIdentity().value,
            guard_evaluator_identity=guard_evaluation.CpnGuardEvaluator().identity.value,
            value_canonicalizer_identity=value_canonicalization.CpnValueCanonicalizerIdentity().value,
            value_canonical_decoder_identity=value_decoding.CpnValueCanonicalDecoderIdentity().value,
            value_expression_canonicalizer_identity=(
                canonical_values.CpnValueExpressionCanonicalizerIdentity().value
            ),
            value_expression_decoder_identity=(
                canonical_value_decoding.CpnValueExpressionCanonicalDecoderIdentity().value
            ),
            guard_canonicalizer_identity=canonical_guards.CpnGuardCanonicalizerIdentity().value,
            guard_decoder_identity=canonical_guard_decoding.CpnGuardCanonicalDecoderIdentity().value,
            expression_variable_collector_identity=(
                expression_collection.CpnExpressionVariableCollectorIdentity().value
            ),
            guard_expression_collector_identity=(
                guard_expression_collection.CpnGuardExpressionCollectorIdentity().value
            ),
            guard_variable_collector_identity=(
                guard_variable_collection.CpnGuardVariableCollectorIdentity().value
            ),
            value_ordering_policy_identity=record_ordering.CpnValueOrderingPolicyIdentity().value,
            token_ordering_policy_identity=markings.CpnTokenOrderingPolicy().identity.value,
            external_output_validator_identity=(
                external_outputs.CpnExternalOutputValidatorIdentity().value
            ),
            input_arc_validator_identity=input_validation.CpnInputArcValidator().identity.value,
            output_arc_validator_identity=output_validation.CpnOutputArcValidator().identity.value,
            complete_enabler_identity=enablement_transitions.CpnTransitionEnabler().identity.value,
            enablement_failure_builder_identity=(
                enablement_failure_building.CpnEnablementFailureBuilder().identity.value
            ),
            enabled_binding_ordering_identity=(
                enablement_ordering.CpnEnabledBindingOrderingPolicy().identity.value
            ),
            binding_selector_identity=selection.CpnBindingSelector().identity.value,
            transition_firer_identity=firing_transitions.CpnTransitionFirer().identity.value,
            token_occurrence_reconstructor_identity=(
                occurrence_reconstruction.CpnTokenOccurrenceReconstructor().identity.value
            ),
            firing_result_identity_deriver_identity=(
                firing_identity.CpnFiringResultIdentityDeriver().identity.value
            ),
            successor_marking_builder_identity=(
                firing_successor.CpnSuccessorMarkingBuilder().identity.value
            ),
            firing_failure_builder_identity=(
                firing_failure_building.CpnFiringFailureBuilder().identity.value
            ),
            shadow_firer_identity=shadow_contracts.CpnShadowFirerIdentity().value,
            shadow_firing_replayer_identity=(
                shadow_replay_contracts.CpnShadowFiringReplayerIdentity().value
            ),
            execution_plan_compiler_identity=(
                plan_compilation.WorkflowExecutionPlanCompiler().identity.value
            ),
            child_definition_exporter_identity=(
                child_export_canonical.WorkflowChildDefinitionExporter().identity.value
            ),
            execution_profile_resolver_identity=(
                WorkflowCpnExecutionProfileResolverIdentity().value
            ),
            semantic_version="0.1",
        )
