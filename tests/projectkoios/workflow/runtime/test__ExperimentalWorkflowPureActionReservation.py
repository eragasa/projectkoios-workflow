"""Verification of bounded experimental predecessor reservation."""

from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from projectkoios.workflow.actions import (
    ExperimentalWorkflowAsciiOutputMappingDescriptor,
    ExperimentalWorkflowFiringRequestCoordinates,
    ExperimentalWorkflowSelectedBindingEncoder,
    ExperimentalWorkflowSelectedBindingEvidence,
    ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionExecutionPlan,
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
    ExperimentalWorkflowPureActionCurrentPredecessor,
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


def _input(payload: bytes = b"{}") -> WorkflowInlinePayload:
    contract = _descriptor().input_contracts[0]
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


def _service() -> tuple[
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalInMemoryPureActionReservationRepository,
]:
    repository = ExperimentalInMemoryPureActionReservationRepository(
        (_predecessor(),)
    )
    return (
        ExperimentalWorkflowPureActionReservationService(repository),
        repository,
    )


def test_reserve_closes_plan_selection_request_and_current_predecessor() -> (
    None
):
    service, _ = _service()
    bindings = _bindings()
    evidence = _evidence()

    first = service.reserve(
        execution_bindings=bindings,
        selected_binding_evidence=evidence,
        coordinates=_coordinates(),
        inputs=(_input(),),
    )
    replay = service.reserve(
        execution_bindings=bindings,
        selected_binding_evidence=evidence,
        coordinates=_coordinates(),
        inputs=(_input(),),
    )

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

    result = service.reserve(
        execution_bindings=_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        inputs=(_input(),),
    )

    assert result.status is ExperimentalWorkflowPureActionReserveStatus.STALE
    assert result.reservation is None
    assert result.request is None


def test_post_owner_revalidation_detects_state_change_and_consumption() -> None:
    service, repository = _service()
    result = service.reserve(
        execution_bindings=_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        inputs=(_input(),),
    )
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
        consumed_repository
    )
    assert consumed_service.revalidate(result.reservation) is (
        ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
    )


def test_in_memory_predecessor_cannot_rewind_and_resurrect_reservation() -> (
    None
):
    service, repository = _service()
    result = service.reserve(
        execution_bindings=_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        inputs=(_input(),),
    )
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
            execution_bindings=_bindings(),
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(attempt=attempt),
            inputs=(_input(),),
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
    first_service, _ = _service()
    changed_service, _ = _service()
    bindings = _bindings()
    evidence = _evidence()

    first = first_service.reserve(
        execution_bindings=bindings,
        selected_binding_evidence=evidence,
        coordinates=_coordinates(),
        inputs=(_input(b"{}"),),
    )
    changed = changed_service.reserve(
        execution_bindings=bindings,
        selected_binding_evidence=evidence,
        coordinates=_coordinates(),
        inputs=(_input(b'{"changed":true}'),),
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
    result = service.reserve(
        execution_bindings=_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        inputs=(_input(),),
    )
    assert result.reservation is not None

    object.__setattr__(
        result.reservation,
        "identity",
        ExperimentalWorkflowPureActionReservationIdentity("0" * 64),
    )
    with pytest.raises(ValueError, match="differs after validation"):
        service.revalidate(result.reservation)


def test_service_rejects_plan_selected_profile_substitution() -> None:
    service, _ = _service()

    with pytest.raises(ValueError, match="profile differs"):
        service.reserve(
            execution_bindings=_bindings(profile="fixture.retained-profile:1"),
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            inputs=(_input(),),
        )
