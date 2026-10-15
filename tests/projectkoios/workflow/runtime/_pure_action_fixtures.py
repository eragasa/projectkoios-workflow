"""Shared synthetic fixtures for experimental pure-action execution tests."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from projectkoios.workflow.actions import (
    ExperimentalWorkflowAsciiOutputMappingDescriptor,
    ExperimentalWorkflowFiringRequestCoordinates,
    ExperimentalWorkflowInputSourceProfileIdentity,
    ExperimentalWorkflowPureActionInputMappingDescriptor,
    ExperimentalWorkflowSelectedBindingEncoder,
    ExperimentalWorkflowSelectedBindingEvidence,
    ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlan,
    ExperimentalWorkflowPureActionCpnPlanFactory,
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionExecutionPlan,
    ExperimentalWorkflowPureActionInputBindings,
    ExperimentalWorkflowPureActionInputPlan,
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionFiringOutcome,
    ExperimentalWorkflowPureActionFiringService,
    ExperimentalWorkflowPureActionInvocationOutcome,
    ExperimentalWorkflowPureActionInvocationService,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingSelector,
    ColoredPetriNetBindingSelectorIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorDefinition,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetEnablementResult,
    ColoredPetriNetEnablementResultIdentity,
    ColoredPetriNetExpressionEvaluatorIdentity,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetOrderingPolicyIdentity,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetSelectionResult,
    ColoredPetriNetToken,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionEnabler,
    ColoredPetriNetTransitionEnablerIdentity,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow.runtime import (
    ExperimentalInMemoryPureActionReservationRepository,
    ExperimentalWorkflowPureActionAdmittedInputs,
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionInputAdmissionFactory,
    ExperimentalWorkflowPureActionInputSourceAuthority,
    ExperimentalWorkflowPureActionInputSourceEvidence,
    ExperimentalWorkflowPureActionInputSourceLoadResult,
    ExperimentalWorkflowPureActionInputSourceLoadStatus,
    ExperimentalWorkflowPureActionInputSourceReference,
    ExperimentalWorkflowPureActionInputSourceRepository,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReservationService,
)
from projectkoios.workflow_sdk import WORKFLOW_SDK_VERSION
from projectkoios.workflow_sdk.firing import (
    Firer,
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowFiringFailed,
    WorkflowFiringRejected,
    WorkflowFiringRequest,
    WorkflowFiringResult,
    WorkflowFiringSucceeded,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowIntegrationIdentity,
    WorkflowIntegrationManifestIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
    WorkflowPayloadCodecIdentity,
    WorkflowPayloadOwnerIdentity,
    WorkflowPayloadRepresentationIdentity,
    WorkflowPayloadSchemaIdentity,
    WorkflowPayloadTypeIdentity,
    WorkflowTransitionIdentity,
)
from projectkoios.workflow_sdk.integration import (
    WorkflowIntegrationManifest,
    WorkflowWorkerIntegration,
)
from projectkoios.workflow_sdk.payloads import (
    WorkflowInlinePayload,
    WorkflowPayloadContract,
)


class _FixtureSourceRepository(
    ExperimentalWorkflowPureActionInputSourceRepository
):
    def __init__(
        self,
        sources: tuple[ExperimentalWorkflowPureActionInputSourceEvidence, ...],
        *,
        failure_status: (
            ExperimentalWorkflowPureActionInputSourceLoadStatus | None
        ) = None,
        raise_error: bool = False,
    ) -> None:
        self._sources = {
            _reference(source).identity: source for source in sources
        }
        self._failure_status = failure_status
        self._raise_error = raise_error
        self._load_count = 0
        self._scheduled_replacement: (
            tuple[int, ExperimentalWorkflowPureActionInputSourceEvidence] | None
        ) = None

    def replace(
        self,
        source: ExperimentalWorkflowPureActionInputSourceEvidence,
    ) -> None:
        self._sources[_reference(source).identity] = source

    def replace_after_loads(
        self,
        loads_before_replacement: int,
        source: ExperimentalWorkflowPureActionInputSourceEvidence,
    ) -> None:
        self._scheduled_replacement = (
            self._load_count + loads_before_replacement + 1,
            source,
        )

    def load(
        self,
        reference: ExperimentalWorkflowPureActionInputSourceReference,
    ) -> ExperimentalWorkflowPureActionInputSourceLoadResult:
        self._load_count += 1
        if (
            self._scheduled_replacement is not None
            and self._scheduled_replacement[0] == self._load_count
        ):
            self.replace(self._scheduled_replacement[1])
            self._scheduled_replacement = None
        if self._raise_error:
            raise RuntimeError("fixture repository error")
        if self._failure_status is not None:
            return ExperimentalWorkflowPureActionInputSourceLoadResult(
                status=self._failure_status,
                reference=reference,
                revision_identity=None,
                evidence=None,
                diagnostics=("fixture_source_failure",),
            )
        source = self._sources.get(reference.identity)
        if source is None:
            return ExperimentalWorkflowPureActionInputSourceLoadResult(
                status=(
                    ExperimentalWorkflowPureActionInputSourceLoadStatus.ABSENT
                ),
                reference=reference,
                revision_identity=None,
                evidence=None,
                diagnostics=("fixture_absent",),
            )
        return ExperimentalWorkflowPureActionInputSourceLoadResult(
            status=ExperimentalWorkflowPureActionInputSourceLoadStatus.LOADED,
            reference=reference,
            revision_identity=(
                ExperimentalWorkflowPureActionInputSourceRevisionIdentity(
                    source.identity.value
                )
            ),
            evidence=source,
            diagnostics=(),
        )


class _FixtureFirer(Firer):
    def __init__(
        self,
        descriptor: WorkflowFirerDescriptor,
        *,
        outcome: str = "succeeded",
        callback: Callable[[], None] | None = None,
    ) -> None:
        self._descriptor = descriptor
        self._outcome = outcome
        self._callback = callback
        self.calls = 0

    @property
    def descriptor(self) -> WorkflowFirerDescriptor:
        return self._descriptor

    def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
        self.calls += 1
        if self._callback is not None:
            self._callback()
        if self._outcome == "error":
            raise RuntimeError("fixture owner error")
        if self._outcome == "mutate_request":
            object.__setattr__(request.inputs[0], "data", b"mutated")
        if self._outcome == "rejected":
            return WorkflowFiringRejected(
                request_identity=request.identity,
                occurrence_identity=request.context.occurrence_identity,
                attempt_identity=request.context.attempt_identity,
                firer_identity=request.firer_identity,
                reason_codes=("fixture_rejected",),
                evidence=(),
            )
        if self._outcome == "failed":
            return WorkflowFiringFailed(
                request_identity=request.identity,
                occurrence_identity=request.context.occurrence_identity,
                attempt_identity=request.context.attempt_identity,
                firer_identity=request.firer_identity,
                failure_codes=("fixture_failed",),
                evidence=(),
            )
        return WorkflowFiringSucceeded(
            request_identity=request.identity,
            occurrence_identity=request.context.occurrence_identity,
            attempt_identity=request.context.attempt_identity,
            firer_identity=request.firer_identity,
            outputs=(
                _payload_for_contract(
                    self._descriptor.output_contracts[0],
                    b"fixture.owner.artifact-set:1",
                ),
            ),
            evidence=(
                _payload_for_contract(
                    self._descriptor.evidence_contracts[0],
                    b'{"artifact_count":1}',
                ),
            ),
        )


class _FixtureWorkerIntegration(WorkflowWorkerIntegration):
    def __init__(
        self,
        manifest_identity: WorkflowIntegrationManifestIdentity,
        firers: tuple[Firer, ...],
        *,
        callback: Callable[[], None] | None = None,
    ) -> None:
        self._manifest_identity = manifest_identity
        self._firers = firers
        self._callback = callback

    @property
    def manifest_identity(self) -> WorkflowIntegrationManifestIdentity:
        return self._manifest_identity

    def firers(self) -> tuple[Firer, ...]:
        if self._callback is not None:
            self._callback()
        return self._firers


@dataclass(slots=True)
class _InvocationFixture:
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs
    reservation_result: ExperimentalWorkflowPureActionReservationResult
    invocation_service: ExperimentalWorkflowPureActionInvocationService
    reservation_service: ExperimentalWorkflowPureActionReservationService
    firer: _FixtureFirer
    integration: _FixtureWorkerIntegration
    predecessor_repository: ExperimentalInMemoryPureActionReservationRepository
    source_repository: _FixtureSourceRepository
    cpn_plan: ExperimentalWorkflowPureActionCpnPlan | None


@dataclass(slots=True)
class _CommitFixture:
    invocation_fixture: _InvocationFixture
    invocation: ExperimentalWorkflowPureActionInvocationOutcome
    firing: ExperimentalWorkflowPureActionFiringOutcome
    definition: ColoredPetriNetDefinition
    marking: ColoredPetriNetMarking


def _contract(role: str, maximum: int) -> WorkflowPayloadContract:
    return WorkflowPayloadContract(
        role=role,
        owner_identity=WorkflowPayloadOwnerIdentity("fixture.owner"),
        payload_type_identity=WorkflowPayloadTypeIdentity(f"fixture.{role}"),
        schema_identity=WorkflowPayloadSchemaIdentity(f"fixture.{role}:1"),
        codec_identity=WorkflowPayloadCodecIdentity(f"fixture.{role}-json:1"),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            "canonical-ascii:1"
            if role == "artifact_set_identity"
            else "canonical-json:1"
        ),
        media_type=f"application/vnd.fixture.{role}.v1+json",
        maximum_byte_length=maximum,
    )


def _descriptor() -> WorkflowFirerDescriptor:
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity("fixture.firer"),
        implementation_identity=WorkflowFirerImplementationIdentity(
            "fixture.firer:1"
        ),
        input_contracts=(_contract("projection_request", 128),),
        output_contracts=(_contract("artifact_set_identity", 256),),
        evidence_contracts=(_contract("artifact_set", 1024),),
        bounds=WorkflowFiringBounds(
            maximum_input_count=1,
            maximum_output_count=1,
            maximum_evidence_count=1,
            maximum_input_bytes=128,
            maximum_output_bytes=256,
            maximum_total_bytes=1280,
            maximum_reason_count=1,
        ),
    )


def _bindings(
    *,
    profile: str | None = None,
) -> ExperimentalWorkflowPureActionExecutionBindings:
    descriptor = _descriptor()
    transition_binding = WorkflowTransitionFirerBinding(
        definition_identity=WorkflowDefinitionIdentity("fixture.definition"),
        transition_identity=WorkflowTransitionIdentity("fixture.transition"),
        firer_identity=descriptor.identity,
        input_roles=("projection_request",),
        output_roles=("artifact_set_identity",),
        binding_version="fixture.binding:1",
    )
    mapping = ExperimentalWorkflowAsciiOutputMappingDescriptor(
        transition_binding=transition_binding,
        firer_descriptor=descriptor,
        output_role="artifact_set_identity",
        external_variable_identity=ColoredPetriNetBindingVariableIdentity(
            "artifact_set_identity"
        ),
        external_value_kind=ColoredPetriNetValueKind.STRING,
        mapping_version="fixture.mapping:1",
    )
    plan = ExperimentalWorkflowPureActionExecutionPlan(
        selected_binding_profile_identity=(
            ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity(
                profile
                or ExperimentalWorkflowSelectedBindingEncoder().profile_identity
            )
        ),
        output_mapping_descriptor=mapping,
    )
    manifest = WorkflowIntegrationManifest(
        integration_identity=WorkflowIntegrationIdentity("fixture.integration"),
        package_name="fixture-integration",
        package_version="1.0.0",
        distribution_sha256="a" * 64,
        sdk_contract_version=WORKFLOW_SDK_VERSION,
        firer_descriptors=(descriptor,),
    )
    return ExperimentalWorkflowPureActionExecutionBindings(
        execution_plan=plan,
        integration_manifest=manifest,
    )


def _evidence() -> ExperimentalWorkflowSelectedBindingEvidence:
    binding = ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity(
            "fixture.transition"
        ),
        assignments=(
            ColoredPetriNetBindingAssignment(
                variable_identity=ColoredPetriNetBindingVariableIdentity(
                    "candidate"
                ),
                value=ColoredPetriNetValue(
                    kind=ColoredPetriNetValueKind.STRING,
                    value="alpha",
                ),
            ),
        ),
    )
    ordering = ColoredPetriNetOrderingPolicyIdentity("fixture.ordering")
    enablement = ColoredPetriNetEnablementResult(
        identity=ColoredPetriNetEnablementResultIdentity("1" * 64),
        definition_identity=ColoredPetriNetDefinitionIdentity(
            "fixture.definition"
        ),
        selection_policy=ColoredPetriNetSelectionPolicy.DETERMINISTIC_ONLY,
        marking_identity=ColoredPetriNetMarkingIdentity("fixture.marking"),
        expression_evaluator_identity=ColoredPetriNetExpressionEvaluatorIdentity(
            "fixture.expression"
        ),
        ordering_policy_identity=ordering,
        transition_enabler_identity=ColoredPetriNetTransitionEnablerIdentity(
            "fixture.enabler"
        ),
        enabled_bindings=(binding,),
    )
    selection = ColoredPetriNetSelectionResult(
        enablement_result_identity=enablement.identity,
        selector_identity=ColoredPetriNetBindingSelectorIdentity(
            "fixture.selector"
        ),
        ordering_policy_identity=ordering,
        outcome=ColoredPetriNetSelectionOutcomeKind.SELECTED,
        selected_binding=binding,
    )
    return ExperimentalWorkflowSelectedBindingEvidence(
        enablement_result=enablement,
        selection_result=selection,
    )


def _coordinates(
    *,
    attempt: str = "fixture.attempt",
    revision: int = 7,
) -> ExperimentalWorkflowFiringRequestCoordinates:
    return ExperimentalWorkflowFiringRequestCoordinates(
        net_instance_identity=WorkflowNetInstanceIdentity("fixture.net"),
        predecessor_marking_identity=WorkflowMarkingIdentity("fixture.marking"),
        predecessor_revision=revision,
        occurrence_identity=WorkflowOccurrenceIdentity("fixture.occurrence"),
        attempt_identity=WorkflowAttemptIdentity(attempt),
        attempt_ordinal=0,
    )


def _transition(
    variable: str = "artifact_set_identity",
) -> ColoredPetriNetTransitionDefinition:
    return ColoredPetriNetTransitionDefinition(
        identity=ColoredPetriNetTransitionIdentity("fixture.transition"),
        input_variable_identities=(),
        external_output_variable_identities=(
            ColoredPetriNetBindingVariableIdentity(variable),
        ),
        guard=ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE),
    )


def _cpn_firing_fixture(
    *,
    color_kind: ColoredPetriNetValueKind = ColoredPetriNetValueKind.STRING,
) -> tuple[
    ColoredPetriNetDefinition,
    ColoredPetriNetMarking,
    ExperimentalWorkflowSelectedBindingEvidence,
]:
    color = ColoredPetriNetColorDefinition(
        ColoredPetriNetColorIdentity("fixture.value"),
        (color_kind,),
    )
    place = ColoredPetriNetPlaceDefinition(
        ColoredPetriNetPlaceIdentity("fixture.place"),
        (color.identity,),
    )
    input_variable = ColoredPetriNetBindingVariableIdentity("candidate")
    output_variable = ColoredPetriNetBindingVariableIdentity(
        "artifact_set_identity"
    )
    transition = ColoredPetriNetTransitionDefinition(
        identity=ColoredPetriNetTransitionIdentity("fixture.transition"),
        input_variable_identities=(input_variable,),
        external_output_variable_identities=(output_variable,),
        guard=ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE),
    )
    input_arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("fixture.input"),
        place.identity,
        transition.identity,
        ColoredPetriNetInputInscription(
            ColoredPetriNetInputMode.CONSUME,
            (
                ColoredPetriNetTokenPattern(
                    input_variable,
                    (color.identity,),
                ),
            ),
        ),
    )
    output_expression = ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.VARIABLE,
        variable_identity=output_variable,
    )
    output_arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("fixture.output"),
        place.identity,
        transition.identity,
        output_inscription=ColoredPetriNetOutputInscription(
            (
                ColoredPetriNetTokenTemplate(
                    color.identity,
                    output_expression,
                ),
            )
        ),
    )
    definition = ColoredPetriNetDefinition(
        ColoredPetriNetDefinitionIdentity("fixture.definition"),
        (color,),
        (place,),
        (transition,),
        (input_arc, output_arc),
        (transition.identity,),
    )
    input_value: str | int = (
        "alpha" if color_kind is (ColoredPetriNetValueKind.STRING) else 1
    )
    marking = ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("fixture.marking"),
        definition.identity,
        (
            ColoredPetriNetPlaceMarking(
                place.identity,
                (
                    ColoredPetriNetToken(
                        color.identity,
                        ColoredPetriNetValue(color_kind, input_value),
                    ),
                ),
            ),
        ),
    )
    enablement = ColoredPetriNetTransitionEnabler().execute(
        definition,
        marking,
    )
    selection = ColoredPetriNetBindingSelector().execute(
        definition,
        enablement,
    )
    return (
        definition,
        marking,
        ExperimentalWorkflowSelectedBindingEvidence(
            enablement_result=enablement,
            selection_result=selection,
        ),
    )


def _payload_for_contract(
    contract: WorkflowPayloadContract,
    payload: bytes = b"{}",
) -> WorkflowInlinePayload:
    return WorkflowInlinePayload(
        role=contract.role,
        owner_identity=contract.owner_identity,
        payload_type_identity=contract.payload_type_identity,
        schema_identity=contract.schema_identity,
        codec_identity=contract.codec_identity,
        representation_identity=contract.representation_identity,
        media_type=contract.media_type,
        payload=payload,
        byte_length=len(payload),
        payload_sha256=hashlib.sha256(payload).hexdigest(),
    )


def _input(payload: bytes = b"{}") -> WorkflowInlinePayload:
    return _payload_for_contract(_descriptor().input_contracts[0], payload)


def _input_bindings(
    *,
    bindings: ExperimentalWorkflowPureActionExecutionBindings | None = None,
    source_kind: str = "retained-inline-payload",
    source_profile: str = "fixture.retained-payload:1",
    mapping_version: str = "fixture.input-mapping:1",
) -> ExperimentalWorkflowPureActionInputBindings:
    execution_bindings = bindings or _bindings()
    input_plan = ExperimentalWorkflowPureActionInputPlan(
        execution_plan=execution_bindings.execution_plan,
        input_mappings=(
            ExperimentalWorkflowPureActionInputMappingDescriptor(
                input_role="projection_request",
                source_kind=source_kind,
                source_profile_identity=(
                    ExperimentalWorkflowInputSourceProfileIdentity(
                        source_profile
                    )
                ),
                mapping_version=mapping_version,
            ),
        ),
    )
    return ExperimentalWorkflowPureActionInputBindings(
        input_plan=input_plan,
        execution_bindings=execution_bindings,
    )


def _two_input_bindings() -> ExperimentalWorkflowPureActionInputBindings:
    contracts = (
        _contract("projection_request", 128),
        _contract("projection_context", 128),
    )
    descriptor = WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity("fixture.two-input-firer"),
        implementation_identity=WorkflowFirerImplementationIdentity(
            "fixture.two-input-firer:1"
        ),
        input_contracts=contracts,
        output_contracts=(_contract("artifact_set_identity", 256),),
        evidence_contracts=(_contract("artifact_set", 1024),),
        bounds=WorkflowFiringBounds(
            maximum_input_count=2,
            maximum_output_count=1,
            maximum_evidence_count=1,
            maximum_input_bytes=256,
            maximum_output_bytes=256,
            maximum_total_bytes=1280,
            maximum_reason_count=1,
        ),
    )
    transition_binding = WorkflowTransitionFirerBinding(
        definition_identity=WorkflowDefinitionIdentity("fixture.definition"),
        transition_identity=WorkflowTransitionIdentity("fixture.transition"),
        firer_identity=descriptor.identity,
        input_roles=tuple(contract.role for contract in contracts),
        output_roles=("artifact_set_identity",),
        binding_version="fixture.two-input-binding:1",
    )
    mapping = ExperimentalWorkflowAsciiOutputMappingDescriptor(
        transition_binding=transition_binding,
        firer_descriptor=descriptor,
        output_role="artifact_set_identity",
        external_variable_identity=ColoredPetriNetBindingVariableIdentity(
            "artifact_set_identity"
        ),
        external_value_kind=ColoredPetriNetValueKind.STRING,
        mapping_version="fixture.mapping:1",
    )
    execution_plan = ExperimentalWorkflowPureActionExecutionPlan(
        selected_binding_profile_identity=(
            ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity(
                ExperimentalWorkflowSelectedBindingEncoder().profile_identity
            )
        ),
        output_mapping_descriptor=mapping,
    )
    execution_bindings = ExperimentalWorkflowPureActionExecutionBindings(
        execution_plan=execution_plan,
        integration_manifest=WorkflowIntegrationManifest(
            integration_identity=WorkflowIntegrationIdentity(
                "fixture.two-input-integration"
            ),
            package_name="fixture-two-input-integration",
            package_version="1.0.0",
            distribution_sha256="b" * 64,
            sdk_contract_version=WORKFLOW_SDK_VERSION,
            firer_descriptors=(descriptor,),
        ),
    )
    mappings = tuple(
        ExperimentalWorkflowPureActionInputMappingDescriptor(
            input_role=contract.role,
            source_kind="retained-inline-payload",
            source_profile_identity=(
                ExperimentalWorkflowInputSourceProfileIdentity(
                    "fixture.retained-payload:1"
                )
            ),
            mapping_version="fixture.input-mapping:1",
        )
        for contract in contracts
    )
    return ExperimentalWorkflowPureActionInputBindings(
        input_plan=ExperimentalWorkflowPureActionInputPlan(
            execution_plan=execution_plan,
            input_mappings=mappings,
        ),
        execution_bindings=execution_bindings,
    )


def _source(
    *,
    payload: bytes = b"{}",
    source_kind: str = "retained-inline-payload",
    source_profile: str = "fixture.retained-payload:1",
    source_identity: str = "fixture.source-evidence",
) -> ExperimentalWorkflowPureActionInputSourceEvidence:
    return ExperimentalWorkflowPureActionInputSourceEvidence(
        source_kind=source_kind,
        source_profile_identity=ExperimentalWorkflowInputSourceProfileIdentity(
            source_profile
        ),
        source_identity=source_identity,
        payload=_input(payload),
    )


def _reference(
    source: ExperimentalWorkflowPureActionInputSourceEvidence | None = None,
) -> ExperimentalWorkflowPureActionInputSourceReference:
    selected = source or _source()
    return ExperimentalWorkflowPureActionInputSourceReference(
        source_kind=selected.source_kind,
        source_profile_identity=selected.source_profile_identity,
        source_identity=selected.source_identity,
    )


def _admitted(
    *,
    input_bindings: ExperimentalWorkflowPureActionInputBindings | None = None,
    evidence: ExperimentalWorkflowSelectedBindingEvidence | None = None,
    coordinates: ExperimentalWorkflowFiringRequestCoordinates | None = None,
    source: ExperimentalWorkflowPureActionInputSourceEvidence | None = None,
) -> ExperimentalWorkflowPureActionAdmittedInputs:
    return ExperimentalWorkflowPureActionInputAdmissionFactory().execute(
        input_bindings=input_bindings or _input_bindings(),
        selected_binding_evidence=evidence or _evidence(),
        coordinates=coordinates or _coordinates(),
        source_evidence=(source or _source(),),
    )


def _authorized(
    admitted: ExperimentalWorkflowPureActionAdmittedInputs | None = None,
) -> ExperimentalWorkflowPureActionAuthorizedInputs:
    selected = admitted or _admitted()
    authorities = tuple(
        ExperimentalWorkflowPureActionInputSourceAuthority(
            reference_identity=(
                ExperimentalWorkflowPureActionInputSourceReference(
                    source_kind=source.source_kind,
                    source_profile_identity=source.source_profile_identity,
                    source_identity=source.source_identity,
                ).identity
            ),
            revision_identity=(
                ExperimentalWorkflowPureActionInputSourceRevisionIdentity(
                    source.identity.value
                )
            ),
            evidence_identity=source.identity,
        )
        for source in selected.source_evidence
    )
    return ExperimentalWorkflowPureActionAuthorizedInputs(
        admitted_inputs=selected,
        source_authorities=authorities,
    )


def _predecessor(
    *,
    marking: str = "fixture.marking",
    revision: int = 7,
) -> ExperimentalWorkflowPureActionCurrentPredecessor:
    return ExperimentalWorkflowPureActionCurrentPredecessor(
        net_instance_identity=WorkflowNetInstanceIdentity("fixture.net"),
        marking_identity=WorkflowMarkingIdentity(marking),
        revision=revision,
    )


def _service(
    *sources: ExperimentalWorkflowPureActionInputSourceEvidence,
    source_repository: _FixtureSourceRepository | None = None,
) -> tuple[
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalInMemoryPureActionReservationRepository,
]:
    repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),)
    )
    retained_source_repository = source_repository or _FixtureSourceRepository(
        sources or (_source(),)
    )
    return (
        ExperimentalWorkflowPureActionReservationService(
            repository,
            retained_source_repository,
        ),
        repository,
    )


def _invocation_fixture(
    *,
    outcome: str = "succeeded",
    stale_during_fire: bool = False,
    change_source_during_fire: bool = False,
    evidence: ExperimentalWorkflowSelectedBindingEvidence | None = None,
    cpn_definition: ColoredPetriNetDefinition | None = None,
) -> _InvocationFixture:
    source = _source()
    authorized = _authorized(_admitted(source=source, evidence=evidence))
    source_repository = _FixtureSourceRepository((source,))
    reservation_service, predecessor_repository = _service(
        source,
        source_repository=source_repository,
    )
    cpn_plan = None
    if cpn_definition is not None:
        cpn_plan = ExperimentalWorkflowPureActionCpnPlanFactory().execute(
            input_plan=authorized.admitted_inputs.input_bindings.input_plan,
            definition=cpn_definition,
            execution_profile=experimental_shadow_cpn_execution_profile(),
        )
    reservation_result = reservation_service.reserve(
        authorized_inputs=authorized,
        cpn_plan=cpn_plan,
    )
    callback: Callable[[], None] | None = None
    if stale_during_fire or change_source_during_fire:

        def make_stale() -> None:
            if stale_during_fire:
                predecessor_repository.advance_current_predecessor(
                    _predecessor(marking="fixture.successor", revision=8)
                )
            if change_source_during_fire:
                source_repository.replace(_source(payload=b'{"changed":true}'))

        callback = make_stale
    execution_bindings = (
        authorized.admitted_inputs.input_bindings.execution_bindings
    )
    output_mapping = execution_bindings.execution_plan.output_mapping_descriptor
    descriptor = output_mapping.firer_descriptor
    firer = _FixtureFirer(
        descriptor,
        outcome=outcome,
        callback=callback,
    )
    manifest = execution_bindings.integration_manifest
    integration = _FixtureWorkerIntegration(manifest.identity, (firer,))
    return _InvocationFixture(
        authorized=authorized,
        reservation_result=reservation_result,
        invocation_service=ExperimentalWorkflowPureActionInvocationService(
            reservation_service
        ),
        reservation_service=reservation_service,
        firer=firer,
        integration=integration,
        predecessor_repository=predecessor_repository,
        source_repository=source_repository,
        cpn_plan=cpn_plan,
    )


def _cpn_plan(
    fixture: _InvocationFixture,
    definition: ColoredPetriNetDefinition,
) -> ExperimentalWorkflowPureActionCpnPlan:
    assert fixture.cpn_plan is not None
    assert fixture.cpn_plan.definition_identity == definition.identity
    return fixture.cpn_plan


def _commit_fixture() -> _CommitFixture:
    definition, marking, evidence = _cpn_firing_fixture()
    fixture = _invocation_fixture(
        evidence=evidence,
        cpn_definition=definition,
    )
    invocation = fixture.invocation_service.execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        integration=fixture.integration,
        transition=definition.transitions[0],
    )
    firing = ExperimentalWorkflowPureActionFiringService(
        fixture.reservation_service
    ).execute(
        authorized_inputs=fixture.authorized,
        reservation_result=fixture.reservation_result,
        invocation_outcome=invocation,
        cpn_plan=_cpn_plan(fixture, definition),
        definition=definition,
        predecessor_marking=marking,
    )
    return _CommitFixture(
        invocation_fixture=fixture,
        invocation=invocation,
        firing=firing,
        definition=definition,
        marking=marking,
    )
