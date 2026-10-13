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
from ..canonical.expressions import guards as canonical_guards
from ..canonical.expressions import values as canonical_values
from ..canonical.firing.results import identity as canonical_firing_identity
from ..children.exports import canonical as child_export_canonical
from ..control.records import canonical as record_canonical
from ..control.records import ordering as record_ordering
from ..control.records import schema as record_schema
from ..control.records.types import graph as record_type_graph
from ..control.records.values import canonicalization as value_canonicalization
from ..control.records.values import decoding as value_decoding
from ..enablement import ordering as enablement_ordering
from ..enablement import transitions as enablement_transitions
from ..enablement.failures import building as enablement_failure_building
from ..expressions import collection as expression_collection
from ..expressions import construction as expression_construction
from ..expressions import evaluation as expression_evaluation
from ..expressions import grammar as expression_grammar
from ..expressions import projection as expression_projection
from ..expressions import validation as expression_validation
from ..firing import transitions as firing_transitions
from ..firing.failures import building as firing_failure_building
from ..firing.markings import successor as firing_successor
from ..firing.occurrences import reconstruction as occurrence_reconstruction
from ..firing.results import identity as firing_identity
from ..outputs import external as external_outputs
from ..plans import definition as plan_definition
from ..shadow import contracts as shadow_contracts
from ..shadow.replay import contracts as shadow_replay_contracts
from ..validation import definitions as definition_validation
from ..validation import markings as marking_validation
from .definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
    WorkflowCpnExecutionProfileResolutionIssue,
    WorkflowCpnExecutionProfileResolutionResult,
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
                expression_validation.CpnExpressionStructureValidatorIdentity().value
            ),
            expression_bounds_validator_identity=(
                expression_validation.CpnExpressionBoundsValidatorIdentity().value
            ),
            field_projector_identity=expression_projection.CpnFieldProjectorIdentity().value,
            control_record_constructor_identity=(
                expression_construction.CpnControlRecordConstructorIdentity().value
            ),
            expression_evaluator_identity=expression_evaluation.CpnExpressionEvaluatorIdentity().value,
            guard_evaluator_identity=expression_evaluation.CpnGuardEvaluator().identity.value,
            value_canonicalizer_identity=value_canonicalization.CpnValueCanonicalizerIdentity().value,
            value_canonical_decoder_identity=value_decoding.CpnValueCanonicalDecoderIdentity().value,
            value_expression_canonicalizer_identity=(
                canonical_values.CpnValueExpressionCanonicalizerIdentity().value
            ),
            value_expression_decoder_identity=(
                canonical_values.CpnValueExpressionCanonicalDecoderIdentity().value
            ),
            guard_canonicalizer_identity=canonical_guards.CpnGuardCanonicalizerIdentity().value,
            guard_decoder_identity=canonical_guards.CpnGuardCanonicalDecoderIdentity().value,
            expression_variable_collector_identity=(
                expression_collection.CpnExpressionVariableCollectorIdentity().value
            ),
            guard_expression_collector_identity=(
                expression_collection.CpnGuardExpressionCollectorIdentity().value
            ),
            guard_variable_collector_identity=(
                expression_collection.CpnGuardVariableCollectorIdentity().value
            ),
            value_ordering_policy_identity=record_ordering.CpnValueOrderingPolicyIdentity().value,
            token_ordering_policy_identity=markings.CpnTokenOrderingPolicy().identity.value,
            external_output_validator_identity=(
                external_outputs.CpnExternalOutputValidatorIdentity().value
            ),
            input_arc_validator_identity=definition_validation.CpnInputArcValidator().identity.value,
            output_arc_validator_identity=definition_validation.CpnOutputArcValidator().identity.value,
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
                plan_definition.WorkflowExecutionPlanCompiler().identity.value
            ),
            child_definition_exporter_identity=(
                child_export_canonical.WorkflowChildDefinitionExporter().identity.value
            ),
            execution_profile_resolver_identity=(
                WorkflowCpnExecutionProfileResolverIdentity().value
            ),
            semantic_version="0.1",
        )


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileResolutionRequest:
    """One complete retained profile requested for local resolution."""

    profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.profile) is not WorkflowCpnExecutionProfile:
            raise TypeError("profile must be WorkflowCpnExecutionProfile")


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileResolverIdentity:
    """Identity of exact local component-resolution semantics."""

    value: str = "projectkoios.workflow.cpn.execution-profile-resolver:0.1"


@final
class WorkflowCpnExecutionProfileResolver:
    """Resolve every retained profile component against local operations."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowCpnExecutionProfileResolverIdentity:
        """Return exact profile-resolution semantics identity."""
        return WorkflowCpnExecutionProfileResolverIdentity()

    def execute(
        self, request: WorkflowCpnExecutionProfileResolutionRequest
    ) -> WorkflowCpnExecutionProfileResolutionResult:
        """Return all unavailable components without resolving by name lookup."""
        if type(request) is not WorkflowCpnExecutionProfileResolutionRequest:
            raise TypeError(
                "request must be WorkflowCpnExecutionProfileResolutionRequest"
            )
        profile = request.profile
        supported = WorkflowCpnExecutionProfileBuilder().execute(
            WorkflowCpnExecutionProfileBuildingRequest()
        )
        issues = tuple(
            WorkflowCpnExecutionProfileResolutionIssue(
                name,
                getattr(profile, name),
                getattr(supported, name),
            )
            for name in sorted(profile.__dataclass_fields__)
            if getattr(profile, name) != getattr(supported, name)
        )
        profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
            WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
        )
        return WorkflowCpnExecutionProfileResolutionResult(
            profile_identity,
            issues,
            None if issues else firing_transitions.CpnTransitionFirer(),
        )
