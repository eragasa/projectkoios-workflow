"""Verification of bounded experimental predecessor reservation."""

from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier

import pytest
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
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionExecutionPlan,
    ExperimentalWorkflowPureActionInputBindings,
    ExperimentalWorkflowPureActionInputPlan,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingSelectorIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetEnablementResult,
    ColoredPetriNetEnablementResultIdentity,
    ColoredPetriNetExpressionEvaluatorIdentity,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetOrderingPolicyIdentity,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetSelectionResult,
    ColoredPetriNetTransitionEnablerIdentity,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow.runtime import (
    ExperimentalInMemoryPureActionReservationRepository,
    ExperimentalWorkflowPureActionAdmittedInputs,
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionInputAdmissionFactory,
    ExperimentalWorkflowPureActionInputAuthorizationService,
    ExperimentalWorkflowPureActionInputAuthorizationStatus,
    ExperimentalWorkflowPureActionInputSourceAuthority,
    ExperimentalWorkflowPureActionInputSourceEvidence,
    ExperimentalWorkflowPureActionInputSourceLoadResult,
    ExperimentalWorkflowPureActionInputSourceLoadStatus,
    ExperimentalWorkflowPureActionInputSourceReference,
    ExperimentalWorkflowPureActionInputSourceRepository,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from projectkoios.workflow_sdk import WORKFLOW_SDK_VERSION
from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowIntegrationIdentity,
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
from projectkoios.workflow_sdk.integration import WorkflowIntegrationManifest
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
    ) -> None:
        self._sources = {
            _reference(source).identity: source for source in sources
        }
        self._failure_status = failure_status

    def load(
        self,
        reference: ExperimentalWorkflowPureActionInputSourceReference,
    ) -> ExperimentalWorkflowPureActionInputSourceLoadResult:
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
) -> tuple[
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalInMemoryPureActionReservationRepository,
]:
    repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),)
    )
    source_repository = _FixtureSourceRepository(sources or (_source(),))
    return (
        ExperimentalWorkflowPureActionReservationService(
            repository,
            source_repository,
        ),
        repository,
    )


def test_authorization_loads_owner_source_and_reservation_revalidates_it() -> (
    None
):
    source = _source(payload=b'{"retained":true}')
    source_repository = _FixtureSourceRepository((source,))
    authorization = ExperimentalWorkflowPureActionInputAuthorizationService(
        source_repository
    ).execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(source),),
    )

    assert authorization.status is (
        ExperimentalWorkflowPureActionInputAuthorizationStatus.AUTHORIZED
    )
    assert authorization.authorized_inputs is not None
    assert (
        authorization.authorized_inputs.admitted_inputs.request.inputs[0]
        == source.payload
    )
    reservation_service, _ = _service(source)
    reserved = reservation_service.reserve(
        authorized_inputs=authorization.authorized_inputs
    )
    assert reserved.status is (
        ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    assert reserved.reservation is not None
    assert reserved.reservation.input_authorization_identity == (
        authorization.authorized_inputs.identity
    )


def test_authorization_fails_closed_for_absent_or_changed_reference() -> None:
    service = ExperimentalWorkflowPureActionInputAuthorizationService(
        _FixtureSourceRepository(())
    )
    absent = service.execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(),),
    )

    assert absent.status is (
        ExperimentalWorkflowPureActionInputAuthorizationStatus.ABSENT
    )
    assert absent.authorized_inputs is None
    with pytest.raises(ValueError, match="kind differs from mapping"):
        service.execute(
            input_bindings=_input_bindings(),
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_references=(
                ExperimentalWorkflowPureActionInputSourceReference(
                    source_kind="caller-supplied-payload",
                    source_profile_identity=(
                        ExperimentalWorkflowInputSourceProfileIdentity(
                            "fixture.retained-payload:1"
                        )
                    ),
                    source_identity="fixture.source-evidence",
                ),
            ),
        )


@pytest.mark.parametrize(
    ("source_status", "authorization_status"),
    (
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.INCOMPATIBLE,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.INCOMPATIBLE,
        ),
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.CORRUPT,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.CORRUPT,
        ),
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.INDETERMINATE,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.INDETERMINATE,
        ),
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.ERROR,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.ERROR,
        ),
    ),
)
def test_authorization_preserves_owner_source_failure_status(
    source_status: ExperimentalWorkflowPureActionInputSourceLoadStatus,
    authorization_status: (
        ExperimentalWorkflowPureActionInputAuthorizationStatus
    ),
) -> None:
    repository = _FixtureSourceRepository(
        (),
        failure_status=source_status,
    )
    authorization = ExperimentalWorkflowPureActionInputAuthorizationService(
        repository
    ).execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(),),
    )

    assert authorization.status is authorization_status
    assert authorization.authorized_inputs is None


def test_input_mapping_tokens_are_bounded() -> None:
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        ExperimentalWorkflowInputSourceProfileIdentity("x" * 513)
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        ExperimentalWorkflowPureActionInputMappingDescriptor(
            input_role="projection_request",
            source_kind="x" * 513,
            source_profile_identity=(
                ExperimentalWorkflowInputSourceProfileIdentity(
                    "fixture.retained-payload:1"
                )
            ),
            mapping_version="fixture.input-mapping:1",
        )

    forged_profile = ExperimentalWorkflowInputSourceProfileIdentity(
        "fixture.retained-payload:1"
    )
    object.__setattr__(forged_profile, "value", "x" * 513)
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        ExperimentalWorkflowPureActionInputMappingDescriptor(
            input_role="projection_request",
            source_kind="retained-inline-payload",
            source_profile_identity=forged_profile,
            mapping_version="fixture.input-mapping:1",
        )


def test_input_plan_and_bindings_content_identify_mapping_semantics() -> None:
    execution_bindings = _bindings()
    first = _input_bindings(bindings=execution_bindings)
    replay = _input_bindings(bindings=execution_bindings)
    changed = _input_bindings(
        bindings=execution_bindings,
        mapping_version="fixture.input-mapping:2",
    )

    assert first == replay
    assert first.identity == replay.identity
    assert first.identity != changed.identity
    assert first.input_plan.identity != changed.input_plan.identity
    assert first.execution_bindings == execution_bindings


def test_admission_binds_source_evidence_and_invocation_coordinates() -> None:
    first = _admitted(source=_source(source_identity="fixture.source-a"))
    changed_source = _admitted(
        source=_source(source_identity="fixture.source-b")
    )
    changed_attempt = _admitted(
        coordinates=_coordinates(attempt="fixture.other-attempt"),
        source=_source(source_identity="fixture.source-a"),
    )

    assert first.request == changed_source.request
    assert first.identity != changed_source.identity
    assert first.request.identity != changed_attempt.request.identity
    assert first.identity != changed_attempt.identity


def test_admission_rejects_source_mapping_and_contract_substitution() -> None:
    with pytest.raises(ValueError, match="kind differs from mapping"):
        _admitted(source=_source(source_kind="caller-supplied-payload"))
    with pytest.raises(ValueError, match="profile differs from mapping"):
        _admitted(source=_source(source_profile="fixture.other-profile:1"))
    with pytest.raises(ValueError, match="exactly satisfy retained contracts"):
        ExperimentalWorkflowPureActionInputAdmissionFactory().execute(
            input_bindings=_input_bindings(),
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=(),
        )

    changed_codec = replace(
        _input(),
        codec_identity=WorkflowPayloadCodecIdentity("fixture.other-codec:1"),
    )
    source = ExperimentalWorkflowPureActionInputSourceEvidence(
        source_kind="retained-inline-payload",
        source_profile_identity=ExperimentalWorkflowInputSourceProfileIdentity(
            "fixture.retained-payload:1"
        ),
        source_identity="fixture.source-evidence",
        payload=changed_codec,
    )
    with pytest.raises(ValueError, match="metadata differs from contract"):
        _admitted(source=source)


def test_admission_rejects_missing_duplicate_and_reordered_inputs() -> None:
    bindings = _two_input_bindings()
    output_mapping = (
        bindings.input_plan.execution_plan.output_mapping_descriptor
    )
    contracts = output_mapping.firer_descriptor.input_contracts
    sources = tuple(
        ExperimentalWorkflowPureActionInputSourceEvidence(
            source_kind="retained-inline-payload",
            source_profile_identity=(
                ExperimentalWorkflowInputSourceProfileIdentity(
                    "fixture.retained-payload:1"
                )
            ),
            source_identity=f"fixture.source-{index}",
            payload=_payload_for_contract(contract),
        )
        for index, contract in enumerate(contracts)
    )
    factory = ExperimentalWorkflowPureActionInputAdmissionFactory()

    with pytest.raises(ValueError, match="exactly satisfy retained contracts"):
        factory.execute(
            input_bindings=bindings,
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=sources[:1],
        )
    with pytest.raises(ValueError, match="metadata differs from contract"):
        factory.execute(
            input_bindings=bindings,
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=(sources[0], sources[0]),
        )
    with pytest.raises(ValueError, match="metadata differs from contract"):
        factory.execute(
            input_bindings=bindings,
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=tuple(reversed(sources)),
        )


def test_admission_rejects_machine_paths_and_direct_identity_forgery() -> None:
    with pytest.raises(ValueError, match="machine path"):
        _source(source_identity="/private/tmp/payload.json")

    admitted = _admitted()
    object.__setattr__(
        admitted,
        "identity",
        ExperimentalWorkflowPureActionAdmittedInputsIdentity("0" * 64),
    )
    with pytest.raises(ValueError, match="admitted inputs differ"):
        _authorized(admitted)

    authorized = _authorized()
    forged_authority = replace(
        authorized.source_authorities[0],
        reference_identity=_reference(
            _source(source_identity="fixture.other-source")
        ).identity,
    )
    with pytest.raises(ValueError, match="differs from admitted source"):
        ExperimentalWorkflowPureActionAuthorizedInputs(
            admitted_inputs=authorized.admitted_inputs,
            source_authorities=(forged_authority,),
        )

    object.__setattr__(
        authorized,
        "identity",
        ExperimentalWorkflowPureActionAuthorizedInputsIdentity("0" * 64),
    )
    reservation_service, _ = _service()
    with pytest.raises(ValueError, match="authorized inputs differ"):
        reservation_service.reserve(authorized_inputs=authorized)


def test_reservation_revalidates_authorized_source_against_repository() -> None:
    claimed_source = _source(payload=b'{"claimed":true}')
    retained_source = _source(payload=b'{"retained":true}')
    service, _ = _service(retained_source)

    result = service.reserve(
        authorized_inputs=_authorized(_admitted(source=claimed_source))
    )

    assert result.status is (
        ExperimentalWorkflowPureActionReserveStatus.SOURCE_CONFLICT
    )
    assert result.reservation is None
    assert result.request is None


def test_source_identity_changes_reservation_even_when_request_is_exact() -> (
    None
):
    first_source = _source(source_identity="fixture.source-a")
    changed_source = _source(source_identity="fixture.source-b")
    first_service, _ = _service(first_source)
    changed_service, _ = _service(changed_source)
    first_admitted = _admitted(source=first_source)
    changed_admitted = _admitted(source=changed_source)

    first = first_service.reserve(authorized_inputs=_authorized(first_admitted))
    changed = changed_service.reserve(
        authorized_inputs=_authorized(changed_admitted)
    )

    assert first.request == changed.request
    assert first.reservation is not None
    assert changed.reservation is not None
    assert first.reservation.identity != changed.reservation.identity
    assert first.reservation.input_admission_identity == first_admitted.identity
    assert (
        changed.reservation.input_admission_identity
        == changed_admitted.identity
    )


def test_earlier_v0_reservation_shapes_remain_reconstructable() -> None:
    admitted = _admitted()
    service, _ = _service()
    result = service.reserve(authorized_inputs=_authorized(admitted))
    assert result.reservation is not None
    current = result.reservation

    legacy = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=current.execution_plan_identity,
        execution_bindings_identity=current.execution_bindings_identity,
        selected_binding_evidence_identity=(
            current.selected_binding_evidence_identity
        ),
        request_identity=current.request_identity,
        net_instance_identity=current.net_instance_identity,
        predecessor_marking_identity=current.predecessor_marking_identity,
        predecessor_revision=current.predecessor_revision,
        occurrence_identity=current.occurrence_identity,
        attempt_identity=current.attempt_identity,
        attempt_ordinal=current.attempt_ordinal,
    )

    admission_bound_shape = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=current.execution_plan_identity,
        execution_bindings_identity=current.execution_bindings_identity,
        selected_binding_evidence_identity=(
            current.selected_binding_evidence_identity
        ),
        request_identity=current.request_identity,
        net_instance_identity=current.net_instance_identity,
        predecessor_marking_identity=current.predecessor_marking_identity,
        predecessor_revision=current.predecessor_revision,
        occurrence_identity=current.occurrence_identity,
        attempt_identity=current.attempt_identity,
        attempt_ordinal=current.attempt_ordinal,
        input_admission_identity=current.input_admission_identity,
    )

    assert legacy.input_admission_identity is None
    assert legacy.input_authorization_identity is None
    assert legacy.identity.value == (
        "2189a0d705aa0523585e434eaa6efc922bcdda1c7535e217c671776a23e9baf7"
    )
    assert admission_bound_shape.input_authorization_identity is None
    assert admission_bound_shape.identity.value == (
        "b25d1dbecb22b1f593c04d3713568ba3dc716b241a1b98121900323fd0d541e2"
    )
    assert legacy.identity != admission_bound_shape.identity
    assert admission_bound_shape.identity != current.identity
    legacy_repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),)
    )
    assert legacy_repository.reserve(legacy) is (
        ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    assert legacy_repository.revalidate(legacy) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_reserve_closes_plan_selection_request_and_current_predecessor() -> (
    None
):
    service, _ = _service()
    bindings = _bindings()
    evidence = _evidence()

    admitted = _admitted(
        input_bindings=_input_bindings(bindings=bindings),
        evidence=evidence,
    )
    authorized = _authorized(admitted)
    first = service.reserve(authorized_inputs=authorized)
    replay = service.reserve(authorized_inputs=authorized)

    assert first.status is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    assert (
        replay.status is ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT
    )
    assert first.reservation == replay.reservation
    assert first.request == replay.request
    assert first.reservation is not None
    assert first.request is not None
    assert (
        first.reservation.execution_plan_identity
        == bindings.execution_plan.identity
    )
    assert first.reservation.execution_bindings_identity == bindings.identity
    assert (
        first.reservation.selected_binding_evidence_identity
        == evidence.identity
    )
    assert first.reservation.request_identity == first.request.identity
    assert first.reservation.input_admission_identity == admitted.identity
    assert first.reservation.input_authorization_identity == authorized.identity
    assert service.revalidate(first.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_stale_predecessor_fails_closed_before_owner_request_is_exposed() -> (
    None
):
    service, repository = _service()
    repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )

    result = service.reserve(authorized_inputs=_authorized())

    assert result.status is ExperimentalWorkflowPureActionReserveStatus.STALE
    assert result.reservation is None
    assert result.request is None


def test_post_owner_revalidation_detects_state_change_and_consumption() -> None:
    service, repository = _service()
    result = service.reserve(authorized_inputs=_authorized())
    assert result.reservation is not None

    repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )
    assert service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.STALE
    )

    consumed_repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),),
        consumed_reservation_identities=(result.reservation.identity,),
    )
    consumed_service = ExperimentalWorkflowPureActionReservationService(
        consumed_repository,
        _FixtureSourceRepository((_source(),)),
    )
    assert consumed_service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
    )


def test_in_memory_predecessor_cannot_rewind_and_resurrect_reservation() -> (
    None
):
    service, repository = _service()
    result = service.reserve(authorized_inputs=_authorized())
    assert result.reservation is not None
    repository.advance_current_predecessor(
        _predecessor(marking="fixture.successor", revision=8)
    )

    with pytest.raises(ValueError, match="revision must advance"):
        repository.advance_current_predecessor(_predecessor())
    assert service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.STALE
    )


def test_concurrent_different_attempts_cannot_reserve_same_predecessor() -> (
    None
):
    service, _ = _service()
    barrier = Barrier(2)

    def reserve(attempt: str) -> ExperimentalWorkflowPureActionReserveStatus:
        barrier.wait()
        return service.reserve(
            authorized_inputs=_authorized(
                _admitted(coordinates=_coordinates(attempt=attempt))
            )
        ).status

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = tuple(
            executor.submit(reserve, attempt)
            for attempt in ("fixture.attempt-a", "fixture.attempt-b")
        )
        statuses = {future.result() for future in futures}

    assert statuses == {
        ExperimentalWorkflowPureActionReserveStatus.RESERVED,
        ExperimentalWorkflowPureActionReserveStatus.CONFLICT,
    }


def test_reservation_identity_changes_with_exact_request_inputs() -> None:
    first_source = _source(payload=b"{}")
    changed_source = _source(payload=b'{"changed":true}')
    first_service, _ = _service(first_source)
    changed_service, _ = _service(changed_source)
    bindings = _bindings()
    evidence = _evidence()

    input_bindings = _input_bindings(bindings=bindings)
    first = first_service.reserve(
        authorized_inputs=_authorized(
            _admitted(
                input_bindings=input_bindings,
                evidence=evidence,
                source=first_source,
            )
        )
    )
    changed = changed_service.reserve(
        authorized_inputs=_authorized(
            _admitted(
                input_bindings=input_bindings,
                evidence=evidence,
                source=changed_source,
            )
        )
    )

    assert first.reservation is not None
    assert changed.reservation is not None
    assert first.reservation.identity != changed.reservation.identity
    assert (
        first.reservation.request_identity
        != changed.reservation.request_identity
    )


def test_repository_rejects_forged_reservation_identity() -> None:
    service, _ = _service()
    result = service.reserve(authorized_inputs=_authorized())
    assert result.reservation is not None

    object.__setattr__(
        result.reservation,
        "identity",
        ExperimentalWorkflowPureActionReservationIdentity("0" * 64),
    )
    with pytest.raises(ValueError, match="differs after validation"):
        service.revalidate(result.reservation)


def test_admission_rejects_plan_selected_profile_substitution() -> None:
    bindings = _bindings(profile="fixture.retained-profile:1")

    with pytest.raises(ValueError, match="profile differs"):
        _admitted(input_bindings=_input_bindings(bindings=bindings))
