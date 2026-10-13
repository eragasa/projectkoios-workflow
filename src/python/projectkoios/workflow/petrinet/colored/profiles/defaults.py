"""Reviewed local CPN execution-profile construction and resolution."""

from dataclasses import dataclass
from typing import final

from ..canonical.bindings import CpnCanonicalBindingCodecIdentity
from ..canonical.definitions import CpnCanonicalDefinitionCodecIdentity
from ..canonical.directives import CpnCanonicalSelectionDirectiveCodecIdentity
from ..canonical.enablement import CpnCanonicalEnablementResultCodecIdentity
from ..canonical.firing_results.identity import (
    CpnCanonicalFiringResultCodecIdentity,
)
from ..canonical.expressions.guards import (
    CpnGuardCanonicalDecoderIdentity,
    CpnGuardCanonicalizerIdentity,
)
from ..canonical.expressions.values import (
    CpnValueExpressionCanonicalDecoderIdentity,
    CpnValueExpressionCanonicalizerIdentity,
)
from ..canonical.json import CpnCanonicalJsonParserIdentity
from ..canonical.markings import CpnCanonicalMarkingCodecIdentity
from ..canonical.selections import CpnCanonicalSelectionResultCodecIdentity
from ..children.exports.canonical import WorkflowChildDefinitionExporter
from ..control.records.canonical import CpnControlRecordCanonicalCodecIdentity
from ..control.records.ordering import CpnValueOrderingPolicyIdentity
from ..control.records.schema import CpnControlRecordSchemaValidatorIdentity
from ..control.records.type_graph import (
    CpnControlRecordTypeGraphValidatorIdentity,
)
from ..control.records.value_canonical import (
    CpnValueCanonicalDecoderIdentity,
    CpnValueCanonicalizerIdentity,
)
from ..enablement.ordering import (
    CpnEnabledBindingOrderingPolicy,
)
from ..enablement.failure_building import (
    CpnEnablementFailureBuilder,
)
from ..enablement.transitions import (
    CpnTransitionEnabler,
)
from ..expressions.collection import (
    CpnExpressionVariableCollectorIdentity,
    CpnGuardExpressionCollectorIdentity,
    CpnGuardVariableCollectorIdentity,
)
from ..expressions.construction import CpnControlRecordConstructorIdentity
from ..expressions.evaluation import (
    CpnExpressionEvaluatorIdentity,
    CpnGuardEvaluator,
)
from ..expressions.grammar import CpnExpressionGrammarIdentity
from ..expressions.projection import CpnFieldProjectorIdentity
from ..expressions.validation import (
    CpnExpressionBoundsValidatorIdentity,
    CpnExpressionStructureValidatorIdentity,
)
from ..external_outputs import (
    CpnExternalOutputValidatorIdentity,
)
from ..firing.failure_building import (
    CpnFiringFailureBuilder,
)
from ..firing.identity_derivation import (
    CpnFiringResultIdentityDeriver,
)
from ..firing.successor_marking import (
    CpnSuccessorMarkingBuilder,
)
from ..firing.occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructor,
)
from ..firing.transitions import (
    CpnTransitionFirer,
)
from ..markings import CpnTokenOrderingPolicy
from ..plans.definition import WorkflowExecutionPlanCompiler
from ..selection import CpnBindingSelector
from ..shadow.contracts import CpnShadowFirerIdentity
from ..shadow.replay_contracts import CpnShadowFiringReplayerIdentity
from ..validation.definitions import (
    CpnDefinitionValidatorIdentity,
    CpnInputArcValidator,
    CpnOutputArcValidator,
)
from ..validation.markings import (
    CpnMarkingValidatorIdentity,
)
from ..values import CpnValueModelIdentity
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
            value_model_identity=CpnValueModelIdentity().value,
            expression_grammar_identity=CpnExpressionGrammarIdentity().value,
            canonical_json_parser_identity=CpnCanonicalJsonParserIdentity().value,
            canonical_definition_codec_identity=(
                CpnCanonicalDefinitionCodecIdentity().value
            ),
            canonical_control_record_codec_identity=(
                CpnControlRecordCanonicalCodecIdentity().value
            ),
            canonical_marking_representation_identity=(
                CpnCanonicalMarkingCodecIdentity().value
            ),
            canonical_binding_representation_identity=(
                CpnCanonicalBindingCodecIdentity().value
            ),
            canonical_directive_representation_identity=(
                CpnCanonicalSelectionDirectiveCodecIdentity().value
            ),
            canonical_enablement_result_representation_identity=(
                CpnCanonicalEnablementResultCodecIdentity().value
            ),
            canonical_selection_result_representation_identity=(
                CpnCanonicalSelectionResultCodecIdentity().value
            ),
            canonical_firing_result_representation_identity=(
                CpnCanonicalFiringResultCodecIdentity().value
            ),
            definition_validator_identity=CpnDefinitionValidatorIdentity().value,
            marking_validator_identity=CpnMarkingValidatorIdentity().value,
            control_record_type_graph_validator_identity=(
                CpnControlRecordTypeGraphValidatorIdentity().value
            ),
            control_record_schema_validator_identity=(
                CpnControlRecordSchemaValidatorIdentity().value
            ),
            expression_structure_validator_identity=(
                CpnExpressionStructureValidatorIdentity().value
            ),
            expression_bounds_validator_identity=(
                CpnExpressionBoundsValidatorIdentity().value
            ),
            field_projector_identity=CpnFieldProjectorIdentity().value,
            control_record_constructor_identity=(
                CpnControlRecordConstructorIdentity().value
            ),
            expression_evaluator_identity=CpnExpressionEvaluatorIdentity().value,
            guard_evaluator_identity=CpnGuardEvaluator().identity.value,
            value_canonicalizer_identity=CpnValueCanonicalizerIdentity().value,
            value_canonical_decoder_identity=CpnValueCanonicalDecoderIdentity().value,
            value_expression_canonicalizer_identity=(
                CpnValueExpressionCanonicalizerIdentity().value
            ),
            value_expression_decoder_identity=(
                CpnValueExpressionCanonicalDecoderIdentity().value
            ),
            guard_canonicalizer_identity=CpnGuardCanonicalizerIdentity().value,
            guard_decoder_identity=CpnGuardCanonicalDecoderIdentity().value,
            expression_variable_collector_identity=(
                CpnExpressionVariableCollectorIdentity().value
            ),
            guard_expression_collector_identity=(
                CpnGuardExpressionCollectorIdentity().value
            ),
            guard_variable_collector_identity=(
                CpnGuardVariableCollectorIdentity().value
            ),
            value_ordering_policy_identity=CpnValueOrderingPolicyIdentity().value,
            token_ordering_policy_identity=CpnTokenOrderingPolicy().identity.value,
            external_output_validator_identity=(
                CpnExternalOutputValidatorIdentity().value
            ),
            input_arc_validator_identity=CpnInputArcValidator().identity.value,
            output_arc_validator_identity=CpnOutputArcValidator().identity.value,
            complete_enabler_identity=CpnTransitionEnabler().identity.value,
            enablement_failure_builder_identity=(
                CpnEnablementFailureBuilder().identity.value
            ),
            enabled_binding_ordering_identity=(
                CpnEnabledBindingOrderingPolicy().identity.value
            ),
            binding_selector_identity=CpnBindingSelector().identity.value,
            transition_firer_identity=CpnTransitionFirer().identity.value,
            token_occurrence_reconstructor_identity=(
                CpnTokenOccurrenceReconstructor().identity.value
            ),
            firing_result_identity_deriver_identity=(
                CpnFiringResultIdentityDeriver().identity.value
            ),
            successor_marking_builder_identity=(
                CpnSuccessorMarkingBuilder().identity.value
            ),
            firing_failure_builder_identity=(
                CpnFiringFailureBuilder().identity.value
            ),
            shadow_firer_identity=CpnShadowFirerIdentity().value,
            shadow_firing_replayer_identity=(
                CpnShadowFiringReplayerIdentity().value
            ),
            execution_plan_compiler_identity=(
                WorkflowExecutionPlanCompiler().identity.value
            ),
            child_definition_exporter_identity=(
                WorkflowChildDefinitionExporter().identity.value
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
            None if issues else CpnTransitionFirer(),
        )
