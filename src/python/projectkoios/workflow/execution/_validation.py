"""Shared trust-boundary reconstruction for pure-action execution."""

from __future__ import annotations

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlan,
)
from projectkoios.workflow.runtime.pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
)
from projectkoios.workflow.runtime.pure_action_reservation import (
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReserveStatus,
)
from projectkoios.workflow_sdk.firing import WorkflowFiringRequest
from projectkoios.workflow_sdk.serialization import (
    WorkflowFiringRequestJsonCodec,
)


def reconstruct_authorized_inputs(
    value: ExperimentalWorkflowPureActionAuthorizedInputs,
) -> ExperimentalWorkflowPureActionAuthorizedInputs:
    """Return an exact reconstructed authorized-input aggregate."""
    if type(value) is not ExperimentalWorkflowPureActionAuthorizedInputs:
        raise TypeError(
            "authorized_inputs must be "
            "ExperimentalWorkflowPureActionAuthorizedInputs"
        )
    reconstructed = ExperimentalWorkflowPureActionAuthorizedInputs(
        admitted_inputs=value.admitted_inputs,
        source_authorities=value.source_authorities,
    )
    if reconstructed != value:
        raise ValueError("authorized inputs differ after validation")
    return reconstructed


def reconstruct_successful_reservation(
    value: ExperimentalWorkflowPureActionReservationResult,
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs,
    *,
    operation: str,
) -> tuple[ExperimentalWorkflowPureActionReservation, WorkflowFiringRequest]:
    """Return a successful reservation correlated to authorized inputs."""
    if type(value) is not ExperimentalWorkflowPureActionReservationResult:
        raise TypeError(
            "reservation_result must be "
            "ExperimentalWorkflowPureActionReservationResult"
        )
    if value.status not in {
        ExperimentalWorkflowPureActionReserveStatus.RESERVED,
        ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT,
    }:
        raise ValueError(f"{operation} requires a successful reservation")
    if value.reservation is None or value.request is None:
        raise ValueError("successful reservation lacks retained records")
    source = value.reservation
    reservation = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=source.execution_plan_identity,
        execution_bindings_identity=source.execution_bindings_identity,
        selected_binding_evidence_identity=(
            source.selected_binding_evidence_identity
        ),
        request_identity=source.request_identity,
        net_instance_identity=source.net_instance_identity,
        predecessor_marking_identity=source.predecessor_marking_identity,
        predecessor_revision=source.predecessor_revision,
        occurrence_identity=source.occurrence_identity,
        attempt_identity=source.attempt_identity,
        attempt_ordinal=source.attempt_ordinal,
        input_admission_identity=source.input_admission_identity,
        input_authorization_identity=source.input_authorization_identity,
        cpn_plan_identity=source.cpn_plan_identity,
    )
    if reservation != source:
        raise ValueError("reservation differs after validation")
    codec = WorkflowFiringRequestJsonCodec()
    request = codec.decode(codec.encode(value.request))
    admitted = authorized.admitted_inputs
    if (
        reservation.input_authorization_identity != authorized.identity
        or reservation.input_admission_identity != admitted.identity
        or reservation.request_identity != request.identity
        or request != admitted.request
    ):
        raise ValueError("reservation differs from authorized inputs")
    return reservation, request


def reconstruct_cpn_plan(
    value: ExperimentalWorkflowPureActionCpnPlan,
) -> ExperimentalWorkflowPureActionCpnPlan:
    """Return one exact reconstructed CPN plan candidate."""
    if type(value) is not ExperimentalWorkflowPureActionCpnPlan:
        raise TypeError(
            "cpn_plan must be ExperimentalWorkflowPureActionCpnPlan"
        )
    reconstructed = ExperimentalWorkflowPureActionCpnPlan(
        input_plan_identity=value.input_plan_identity,
        definition_identity=value.definition_identity,
        definition_representation_profile_identity=(
            value.definition_representation_profile_identity
        ),
        definition_bytes=value.definition_bytes,
        execution_profile=value.execution_profile,
    )
    if reconstructed != value:
        raise ValueError("CPN plan differs after validation")
    return reconstructed


__all__ = [
    "reconstruct_authorized_inputs",
    "reconstruct_cpn_plan",
    "reconstruct_successful_reservation",
]
