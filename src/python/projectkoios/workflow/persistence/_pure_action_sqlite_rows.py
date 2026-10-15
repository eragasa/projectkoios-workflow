"""Pure-action SQLite row reconstruction and integrity codecs."""

from __future__ import annotations

import hashlib

from projectkoios.workflow.actions import (
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
)
from projectkoios.workflow.runtime.pure_action_commit_serialization import (
    ExperimentalWorkflowPureActionCommitEventJsonCodec,
)
from projectkoios.workflow.runtime.pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceAuthority,
    ExperimentalWorkflowPureActionInputSourceAuthorityIdentity,
)
from projectkoios.workflow.runtime.pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceEvidenceIdentity,
)
from projectkoios.workflow.runtime.pure_action_reservation import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
)
from projectkoios.workflow.runtime.pure_action_source_repository import (
    ExperimentalWorkflowPureActionInputSourceReferenceIdentity,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)

from ._sqlite_private import SQLiteStoreFault as _StoreFault


def _reconstruct_reservation(
    value: ExperimentalWorkflowPureActionReservation,
) -> ExperimentalWorkflowPureActionReservation:
    if type(value) is not ExperimentalWorkflowPureActionReservation:
        raise TypeError(
            "reservation must be ExperimentalWorkflowPureActionReservation"
        )
    reconstructed = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=value.execution_plan_identity,
        execution_bindings_identity=value.execution_bindings_identity,
        selected_binding_evidence_identity=value.selected_binding_evidence_identity,
        request_identity=value.request_identity,
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        occurrence_identity=value.occurrence_identity,
        attempt_identity=value.attempt_identity,
        attempt_ordinal=value.attempt_ordinal,
        input_admission_identity=value.input_admission_identity,
        input_authorization_identity=value.input_authorization_identity,
        cpn_plan_identity=value.cpn_plan_identity,
    )
    if reconstructed != value:
        raise ValueError("reservation differs after validation")
    return reconstructed


def _reconstruct_coordinates(
    value: ExperimentalWorkflowPureActionCommitCoordinates,
) -> ExperimentalWorkflowPureActionCommitCoordinates:
    if type(value) is not ExperimentalWorkflowPureActionCommitCoordinates:
        raise TypeError(
            "coordinates must be "
            "ExperimentalWorkflowPureActionCommitCoordinates"
        )
    reconstructed = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=value.commit_identity,
        reservation_identity=value.reservation_identity,
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        successor_marking_identity=value.successor_marking_identity,
        successor_revision=value.successor_revision,
    )
    if reconstructed != value:
        raise ValueError("commit coordinates differ after validation")
    return reconstructed


def _reconstruct_record(
    value: ExperimentalWorkflowPureActionCommitRecord,
) -> ExperimentalWorkflowPureActionCommitRecord:
    if type(value) is not ExperimentalWorkflowPureActionCommitRecord:
        raise TypeError(
            "record must be ExperimentalWorkflowPureActionCommitRecord"
        )
    reconstructed = ExperimentalWorkflowPureActionCommitRecord(
        commit_identity=value.commit_identity,
        cpn_plan_identity=value.cpn_plan_identity,
        reservation_identity=value.reservation_identity,
        net_instance_identity=value.net_instance_identity,
        input_authorization_identity=value.input_authorization_identity,
        source_authorities=value.source_authorities,
        invocation_outcome_identity=value.invocation_outcome_identity,
        request_identity=value.request_identity,
        owner_result_identity=value.owner_result_identity,
        mapped_result_identity=value.mapped_result_identity,
        firing_outcome_identity=value.firing_outcome_identity,
        cpn_firing_result_identity=value.cpn_firing_result_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        successor_marking_identity=value.successor_marking_identity,
        successor_revision=value.successor_revision,
    )
    if reconstructed != value:
        raise ValueError("commit record differs after validation")
    return reconstructed


def _validate_commit_correlations(
    reservation: ExperimentalWorkflowPureActionReservation,
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
    record: ExperimentalWorkflowPureActionCommitRecord,
) -> None:
    if (
        coordinates.reservation_identity != reservation.identity
        or coordinates.net_instance_identity
        != reservation.net_instance_identity
        or coordinates.predecessor_marking_identity
        != reservation.predecessor_marking_identity
        or coordinates.predecessor_revision != reservation.predecessor_revision
        or record.commit_identity != coordinates.commit_identity
        or record.reservation_identity != reservation.identity
        or record.net_instance_identity != reservation.net_instance_identity
        or record.net_instance_identity != coordinates.net_instance_identity
        or record.cpn_plan_identity != reservation.cpn_plan_identity
        or record.input_authorization_identity
        != reservation.input_authorization_identity
        or record.predecessor_marking_identity
        != coordinates.predecessor_marking_identity
        or record.predecessor_revision != coordinates.predecessor_revision
        or record.successor_marking_identity
        != coordinates.successor_marking_identity
        or record.successor_revision != coordinates.successor_revision
    ):
        raise ValueError("commit state differs from reservation")


def _reservation_values(
    value: ExperimentalWorkflowPureActionReservation,
) -> tuple[object, ...]:
    return (
        value.identity.value,
        value.execution_plan_identity.value,
        value.execution_bindings_identity.value,
        value.selected_binding_evidence_identity.value,
        value.request_identity.value,
        value.net_instance_identity.value,
        value.predecessor_marking_identity.value,
        value.predecessor_revision,
        value.occurrence_identity.value,
        value.attempt_identity.value,
        value.attempt_ordinal,
        None
        if value.input_admission_identity is None
        else value.input_admission_identity.value,
        None
        if value.input_authorization_identity is None
        else value.input_authorization_identity.value,
        None
        if value.cpn_plan_identity is None
        else value.cpn_plan_identity.value,
    )


def _reservation_from_row(
    row: tuple[object, ...],
) -> ExperimentalWorkflowPureActionReservation:
    if len(row) != 14:
        raise _StoreFault("invalid_reservation_shape")
    identity = _required_text(row[0], "reservation_identity")
    admission = _optional_text(row[11], "input_admission_identity")
    authorization = _optional_text(row[12], "input_authorization_identity")
    cpn_plan = _optional_text(row[13], "cpn_plan_identity")
    try:
        reservation = ExperimentalWorkflowPureActionReservation(
            execution_plan_identity=ExperimentalWorkflowPureActionExecutionPlanIdentity(
                _required_text(row[1], "execution_plan_identity")
            ),
            execution_bindings_identity=ExperimentalWorkflowPureActionExecutionBindingsIdentity(
                _required_text(row[2], "execution_bindings_identity")
            ),
            selected_binding_evidence_identity=ExperimentalWorkflowSelectedBindingEvidenceIdentity(
                _required_text(row[3], "selected_binding_evidence_identity")
            ),
            request_identity=WorkflowFiringRequestIdentity(
                _required_text(row[4], "request_identity")
            ),
            net_instance_identity=WorkflowNetInstanceIdentity(
                _required_text(row[5], "net_instance_identity")
            ),
            predecessor_marking_identity=WorkflowMarkingIdentity(
                _required_text(row[6], "predecessor_marking_identity")
            ),
            predecessor_revision=_required_int(row[7], "predecessor_revision"),
            occurrence_identity=WorkflowOccurrenceIdentity(
                _required_text(row[8], "occurrence_identity")
            ),
            attempt_identity=WorkflowAttemptIdentity(
                _required_text(row[9], "attempt_identity")
            ),
            attempt_ordinal=_required_int(row[10], "attempt_ordinal"),
            input_admission_identity=(
                None
                if admission is None
                else ExperimentalWorkflowPureActionAdmittedInputsIdentity(
                    admission
                )
            ),
            input_authorization_identity=(
                None
                if authorization is None
                else ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                    authorization
                )
            ),
            cpn_plan_identity=(
                None
                if cpn_plan is None
                else ExperimentalWorkflowPureActionCpnPlanIdentity(cpn_plan)
            ),
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_reservation") from error
    if reservation.identity.value != identity:
        raise _StoreFault("reservation_identity_mismatch")
    return reservation


def _commit_values(
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
    record: ExperimentalWorkflowPureActionCommitRecord,
    net_instance_identity: WorkflowNetInstanceIdentity,
) -> tuple[object, ...]:
    return (
        record.reservation_identity.value,
        record.commit_identity.value,
        net_instance_identity.value,
        record.cpn_plan_identity.value,
        record.input_authorization_identity.value,
        record.invocation_outcome_identity,
        record.request_identity.value,
        record.owner_result_identity.value,
        record.mapped_result_identity,
        record.firing_outcome_identity,
        record.cpn_firing_result_identity,
        coordinates.predecessor_marking_identity.value,
        coordinates.predecessor_revision,
        coordinates.successor_marking_identity.value,
        coordinates.successor_revision,
        ExperimentalWorkflowPureActionCommitEventJsonCodec().encode(record),
        _record_digest(record, net_instance_identity),
    )


def _commit_identity_from_row(row: tuple[object, ...]) -> str:
    if len(row) != 17:
        raise _StoreFault("invalid_commit_shape")
    return _required_text(row[1], "commit_identity")


def _commit_from_rows(
    row: tuple[object, ...],
    authority_rows: tuple[tuple[object, ...], ...],
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
) -> tuple[
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitRecord,
    bytes,
]:
    commit_identity = _commit_identity_from_row(row)
    authorities = tuple(
        _authority_from_row(authority_row, expected_ordinal)
        for expected_ordinal, authority_row in enumerate(authority_rows)
    )
    try:
        net_instance = WorkflowNetInstanceIdentity(
            _required_text(row[2], "net_instance_identity")
        )
        record = ExperimentalWorkflowPureActionCommitRecord(
            commit_identity=ExperimentalWorkflowPureActionCommitIdentity(
                commit_identity
            ),
            cpn_plan_identity=ExperimentalWorkflowPureActionCpnPlanIdentity(
                _required_text(row[3], "cpn_plan_identity")
            ),
            reservation_identity=ExperimentalWorkflowPureActionReservationIdentity(
                _required_text(row[0], "reservation_identity")
            ),
            net_instance_identity=net_instance,
            input_authorization_identity=ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                _required_text(row[4], "input_authorization_identity")
            ),
            source_authorities=authorities,
            invocation_outcome_identity=_required_text(
                row[5], "invocation_outcome_identity"
            ),
            request_identity=WorkflowFiringRequestIdentity(
                _required_text(row[6], "request_identity")
            ),
            owner_result_identity=WorkflowFiringResultIdentity(
                _required_text(row[7], "owner_result_identity")
            ),
            mapped_result_identity=_required_text(
                row[8], "mapped_result_identity"
            ),
            firing_outcome_identity=_required_text(
                row[9], "firing_outcome_identity"
            ),
            cpn_firing_result_identity=_required_text(
                row[10], "cpn_firing_result_identity"
            ),
            predecessor_marking_identity=WorkflowMarkingIdentity(
                _required_text(row[11], "predecessor_marking_identity")
            ),
            predecessor_revision=_required_int(row[12], "predecessor_revision"),
            successor_marking_identity=WorkflowMarkingIdentity(
                _required_text(row[13], "successor_marking_identity")
            ),
            successor_revision=_required_int(row[14], "successor_revision"),
        )
        coordinates = ExperimentalWorkflowPureActionCommitCoordinates(
            commit_identity=record.commit_identity,
            reservation_identity=record.reservation_identity,
            net_instance_identity=net_instance,
            predecessor_marking_identity=record.predecessor_marking_identity,
            predecessor_revision=record.predecessor_revision,
            successor_marking_identity=record.successor_marking_identity,
            successor_revision=record.successor_revision,
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_commit") from error
    event = row[15]
    digest = row[16]
    if type(event) is not bytes:
        raise _StoreFault("invalid_commit_event")
    try:
        decoded_event = (
            ExperimentalWorkflowPureActionCommitEventJsonCodec().decode(event)
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_commit_event") from error
    if decoded_event != record:
        raise _StoreFault("commit_event_record_mismatch")
    if type(digest) is not bytes or digest != _record_digest(
        record, net_instance
    ):
        raise _StoreFault("commit_record_digest_mismatch")
    if record.reservation_identity != reservation_identity:
        raise _StoreFault("commit_reservation_mismatch")
    return coordinates, record, event


def _authority_from_row(
    row: tuple[object, ...],
    expected_ordinal: int,
) -> ExperimentalWorkflowPureActionInputSourceAuthority:
    if (
        len(row) != 5
        or _required_int(row[0], "authority_ordinal") != expected_ordinal
    ):
        raise _StoreFault("invalid_source_authority_order")
    identity = _required_text(row[1], "authority_identity")
    try:
        authority = ExperimentalWorkflowPureActionInputSourceAuthority(
            reference_identity=ExperimentalWorkflowPureActionInputSourceReferenceIdentity(
                _required_text(row[2], "reference_identity")
            ),
            revision_identity=ExperimentalWorkflowPureActionInputSourceRevisionIdentity(
                _required_text(row[3], "revision_identity")
            ),
            evidence_identity=ExperimentalWorkflowPureActionInputSourceEvidenceIdentity(
                _required_text(row[4], "evidence_identity")
            ),
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_source_authority") from error
    if (
        authority.identity
        != ExperimentalWorkflowPureActionInputSourceAuthorityIdentity(identity)
    ):
        raise _StoreFault("source_authority_identity_mismatch")
    return authority


def _predecessor_from_row(
    row: tuple[object, ...],
) -> ExperimentalWorkflowPureActionCurrentPredecessor:
    if len(row) != 4:
        raise _StoreFault("invalid_predecessor_shape")
    try:
        predecessor = ExperimentalWorkflowPureActionCurrentPredecessor(
            net_instance_identity=WorkflowNetInstanceIdentity(
                _required_text(row[0], "net_instance_identity")
            ),
            marking_identity=WorkflowMarkingIdentity(
                _required_text(row[1], "marking_identity")
            ),
            revision=_required_int(row[2], "revision"),
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_predecessor") from error
    digest = row[3]
    if type(digest) is not bytes or digest != _predecessor_digest(
        predecessor.net_instance_identity,
        predecessor.marking_identity,
        predecessor.revision,
    ):
        raise _StoreFault("predecessor_digest_mismatch")
    return predecessor


def _predecessor_digest(
    net_instance_identity: WorkflowNetInstanceIdentity,
    marking_identity: WorkflowMarkingIdentity,
    revision: int,
) -> bytes:
    digest = hashlib.sha256(
        b"projectkoios.workflow.experimental-current-predecessor:0\x00"
    )
    for value in (
        net_instance_identity.value,
        marking_identity.value,
        str(revision),
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.digest()


def _record_digest(
    record: ExperimentalWorkflowPureActionCommitRecord,
    net_instance_identity: WorkflowNetInstanceIdentity,
) -> bytes:
    digest = hashlib.sha256(
        b"projectkoios.workflow.experimental-pure-action-commit-record:0\x00"
    )
    for value in (
        record.commit_identity.value,
        record.cpn_plan_identity.value,
        record.reservation_identity.value,
        record.input_authorization_identity.value,
        net_instance_identity.value,
        record.invocation_outcome_identity,
        record.request_identity.value,
        record.owner_result_identity.value,
        record.mapped_result_identity,
        record.firing_outcome_identity,
        record.cpn_firing_result_identity,
        record.predecessor_marking_identity.value,
        str(record.predecessor_revision),
        record.successor_marking_identity.value,
        str(record.successor_revision),
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    for authority in record.source_authorities:
        for value in (
            authority.identity.value,
            authority.reference_identity.value,
            authority.revision_identity.value,
            authority.evidence_identity.value,
        ):
            encoded = value.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
    return digest.digest()


def _required_text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise _StoreFault(f"invalid_{label}")
    return value


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)


def _required_int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise _StoreFault(f"invalid_{label}")
    return value


__all__ = []
