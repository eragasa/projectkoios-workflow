"""In-memory repository for experimental pure-action reservations."""

from __future__ import annotations

from threading import Lock
from typing import final

from projectkoios.workflow_sdk.identities import (
    WorkflowNetInstanceIdentity,
)

from ._pure_action_reservation_port import (
    ExperimentalWorkflowPureActionReservationRepository,
)
from ._pure_action_reservation_records import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitReadResult,
    ExperimentalWorkflowPureActionCommitReadStatus,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCommittedSnapshot,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)


@final
class ExperimentalInMemoryPureActionReservationRepository(
    ExperimentalWorkflowPureActionReservationRepository
):
    """Thread-safe non-durable reference used as software evidence."""

    __slots__ = (
        "_active",
        "_commit_records",
        "_commits",
        "_consumed",
        "_current",
        "_lock",
    )

    def __init__(
        self,
        predecessors: tuple[
            ExperimentalWorkflowPureActionCurrentPredecessor, ...
        ],
        *,
        consumed_reservation_identities: tuple[
            ExperimentalWorkflowPureActionReservationIdentity, ...
        ] = (),
        committed_coordinates: tuple[
            ExperimentalWorkflowPureActionCommitCoordinates, ...
        ] = (),
        committed_records: tuple[
            ExperimentalWorkflowPureActionCommitRecord, ...
        ] = (),
    ) -> None:
        if type(predecessors) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCurrentPredecessor
            for item in predecessors
        ):
            raise TypeError(
                "predecessors must contain current predecessor records"
            )
        if type(consumed_reservation_identities) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionReservationIdentity
            for item in consumed_reservation_identities
        ):
            raise TypeError(
                "consumed_reservation_identities must contain reservation "
                "identities"
            )
        if type(committed_coordinates) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCommitCoordinates
            for item in committed_coordinates
        ):
            raise TypeError(
                "committed_coordinates must contain "
                "ExperimentalWorkflowPureActionCommitCoordinates"
            )
        if type(committed_records) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCommitRecord
            for item in committed_records
        ):
            raise TypeError(
                "committed_records must contain "
                "ExperimentalWorkflowPureActionCommitRecord"
            )
        identities = tuple(item.net_instance_identity for item in predecessors)
        if len(identities) != len(set(identities)):
            raise ValueError("current predecessor net instances must be unique")
        if len(consumed_reservation_identities) != len(
            set(consumed_reservation_identities)
        ):
            raise ValueError("consumed reservation identities must be unique")
        self._current = {
            item.net_instance_identity: item for item in predecessors
        }
        self._active: dict[
            WorkflowNetInstanceIdentity,
            ExperimentalWorkflowPureActionReservation,
        ] = {}
        commit_reservations = tuple(
            item.reservation_identity for item in committed_coordinates
        )
        commit_identities = tuple(
            item.commit_identity for item in committed_coordinates
        )
        if len(commit_reservations) != len(set(commit_reservations)):
            raise ValueError("committed reservation identities must be unique")
        if len(commit_identities) != len(set(commit_identities)):
            raise ValueError("commit identities must be unique")
        self._commits = {
            item.reservation_identity: item for item in committed_coordinates
        }
        record_reservations = tuple(
            item.reservation_identity for item in committed_records
        )
        if len(record_reservations) != len(set(record_reservations)):
            raise ValueError(
                "commit record reservation identities must be unique"
            )
        self._commit_records = {
            item.reservation_identity: item for item in committed_records
        }
        for reservation_identity, record in self._commit_records.items():
            coordinates = self._commits.get(reservation_identity)
            if coordinates is None or not _record_matches_coordinates(
                record, coordinates
            ):
                raise ValueError(
                    "commit records must exactly match committed coordinates"
                )
        self._consumed = set(consumed_reservation_identities) | set(
            commit_reservations
        )
        self._lock = Lock()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalInMemoryPureActionReservationRepository "
            "is not subclassable"
        )

    def reserve(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionReserveStatus:
        validated = _reconstruct_reservation(reservation)
        with self._lock:
            if not self._matches_current(validated):
                return ExperimentalWorkflowPureActionReserveStatus.STALE
            existing = self._active.get(validated.net_instance_identity)
            if existing is not None:
                if existing == validated:
                    return (
                        ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT
                    )
                return ExperimentalWorkflowPureActionReserveStatus.CONFLICT
            if validated.identity in self._consumed:
                return ExperimentalWorkflowPureActionReserveStatus.CONFLICT
            self._active[validated.net_instance_identity] = validated
            return ExperimentalWorkflowPureActionReserveStatus.RESERVED

    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        validated = _reconstruct_reservation(reservation)
        with self._lock:
            if validated.identity in self._consumed:
                return ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
            if self._active.get(validated.net_instance_identity) != validated:
                return ExperimentalWorkflowPureActionRevalidationStatus.ABSENT
            if not self._matches_current(validated):
                return ExperimentalWorkflowPureActionRevalidationStatus.STALE
            return ExperimentalWorkflowPureActionRevalidationStatus.CURRENT

    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically retain compact commit state and advance the marking."""
        validated_reservation = _reconstruct_reservation(reservation)
        validated_coordinates = _reconstruct_commit_coordinates(coordinates)
        validated_record = (
            None if record is None else _reconstruct_commit_record(record)
        )
        if (
            validated_coordinates.reservation_identity
            != validated_reservation.identity
            or validated_coordinates.net_instance_identity
            != validated_reservation.net_instance_identity
            or validated_coordinates.predecessor_marking_identity
            != validated_reservation.predecessor_marking_identity
            or validated_coordinates.predecessor_revision
            != validated_reservation.predecessor_revision
        ):
            raise ValueError("commit coordinates differ from reservation")
        if validated_record is not None and (
            validated_record.reservation_identity
            != validated_reservation.identity
            or not _record_matches_coordinates(
                validated_record, validated_coordinates
            )
        ):
            raise ValueError("commit record differs from commit coordinates")
        with self._lock:
            existing = self._commits.get(validated_reservation.identity)
            if existing is not None:
                existing_record = self._commit_records.get(
                    validated_reservation.identity
                )
                if existing == validated_coordinates and (
                    validated_record is None
                    or existing_record == validated_record
                ):
                    return ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            if any(
                item.commit_identity == validated_coordinates.commit_identity
                for item in self._commits.values()
            ):
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            if not self._matches_current(validated_reservation):
                return ExperimentalWorkflowPureActionCommitStatus.STALE
            if (
                self._active.get(validated_reservation.net_instance_identity)
                != validated_reservation
                or validated_reservation.identity in self._consumed
            ):
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            active = dict(self._active)
            current = dict(self._current)
            consumed = set(self._consumed)
            commits = dict(self._commits)
            commit_records = dict(self._commit_records)
            del active[validated_reservation.net_instance_identity]
            consumed.add(validated_reservation.identity)
            commits[validated_reservation.identity] = validated_coordinates
            if validated_record is not None:
                commit_records[validated_reservation.identity] = (
                    validated_record
                )
            current[validated_reservation.net_instance_identity] = (
                ExperimentalWorkflowPureActionCurrentPredecessor(
                    net_instance_identity=(
                        validated_reservation.net_instance_identity
                    ),
                    marking_identity=(
                        validated_coordinates.successor_marking_identity
                    ),
                    revision=validated_coordinates.successor_revision,
                )
            )
            active, current, consumed, commits = _finalize_commit_state(
                active,
                current,
                consumed,
                commits,
            )
            self._active = active
            self._current = current
            self._consumed = consumed
            self._commits = commits
            self._commit_records = commit_records
            return ExperimentalWorkflowPureActionCommitStatus.COMMITTED

    def load_committed_snapshot(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitReadResult:
        """Atomically reconstruct one retained in-memory commit snapshot."""
        if type(reservation_identity) is not (
            ExperimentalWorkflowPureActionReservationIdentity
        ):
            raise TypeError(
                "reservation_identity must be "
                "ExperimentalWorkflowPureActionReservationIdentity"
            )
        with self._lock:
            coordinates = self._commits.get(reservation_identity)
            record = self._commit_records.get(reservation_identity)
        if coordinates is None and record is None:
            return _commit_read_failure(
                ExperimentalWorkflowPureActionCommitReadStatus.ABSENT,
                "commit_absent",
            )
        if coordinates is None or record is None:
            return _commit_read_failure(
                ExperimentalWorkflowPureActionCommitReadStatus.CORRUPT,
                "incomplete_commit_state",
            )
        from .pure_action_commit_serialization import (
            ExperimentalWorkflowPureActionCommitEventJsonCodec,
        )

        try:
            snapshot = ExperimentalWorkflowPureActionCommittedSnapshot(
                coordinates=coordinates,
                record=record,
                event_bytes=(
                    ExperimentalWorkflowPureActionCommitEventJsonCodec().encode(
                        record
                    )
                ),
            )
        except TypeError, ValueError:
            return _commit_read_failure(
                ExperimentalWorkflowPureActionCommitReadStatus.CORRUPT,
                "commit_snapshot_invalid",
            )
        return ExperimentalWorkflowPureActionCommitReadResult(
            status=ExperimentalWorkflowPureActionCommitReadStatus.FOUND,
            snapshot=snapshot,
            diagnostics=(),
        )

    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load exact retained coordinates without exposing mutable state."""
        result = self.load_committed_snapshot(reservation_identity)
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.FOUND
        ):
            assert result.snapshot is not None
            return result.snapshot.coordinates
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.ABSENT
        ):
            return None
        raise RuntimeError(result.diagnostics[0])

    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the complete compact retained commit record."""
        result = self.load_committed_snapshot(reservation_identity)
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.FOUND
        ):
            assert result.snapshot is not None
            return result.snapshot.record
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.ABSENT
        ):
            return None
        raise RuntimeError(result.diagnostics[0])

    def load_commit_event(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> bytes | None:
        """Construct canonical event bytes for retained in-memory evidence."""
        result = self.load_committed_snapshot(reservation_identity)
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.FOUND
        ):
            assert result.snapshot is not None
            return result.snapshot.event_bytes
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.ABSENT
        ):
            return None
        raise RuntimeError(result.diagnostics[0])

    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the current compact marking coordinate."""
        if type(net_instance_identity) is not WorkflowNetInstanceIdentity:
            raise TypeError(
                "net_instance_identity must be WorkflowNetInstanceIdentity"
            )
        with self._lock:
            return self._current.get(net_instance_identity)

    def advance_current_predecessor(
        self,
        predecessor: ExperimentalWorkflowPureActionCurrentPredecessor,
    ) -> None:
        """Advance one current coordinate without permitting revision rewind."""
        if (
            type(predecessor)
            is not ExperimentalWorkflowPureActionCurrentPredecessor
        ):
            raise TypeError(
                "predecessor must be "
                "ExperimentalWorkflowPureActionCurrentPredecessor"
            )
        with self._lock:
            current = self._current.get(predecessor.net_instance_identity)
            if current is not None and predecessor.revision <= current.revision:
                raise ValueError("current predecessor revision must advance")
            self._current[predecessor.net_instance_identity] = predecessor

    def _matches_current(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> bool:
        current = self._current.get(reservation.net_instance_identity)
        return current == ExperimentalWorkflowPureActionCurrentPredecessor(
            net_instance_identity=reservation.net_instance_identity,
            marking_identity=reservation.predecessor_marking_identity,
            revision=reservation.predecessor_revision,
        )


def _commit_read_failure(
    status: ExperimentalWorkflowPureActionCommitReadStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCommitReadResult:
    return ExperimentalWorkflowPureActionCommitReadResult(
        status=status,
        snapshot=None,
        diagnostics=(diagnostic,),
    )


def _reconstruct_commit_coordinates(
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


def _reconstruct_commit_record(
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


def _record_matches_coordinates(
    record: ExperimentalWorkflowPureActionCommitRecord,
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
) -> bool:
    return (
        record.commit_identity == coordinates.commit_identity
        and record.reservation_identity == coordinates.reservation_identity
        and record.net_instance_identity == coordinates.net_instance_identity
        and record.predecessor_marking_identity
        == coordinates.predecessor_marking_identity
        and record.predecessor_revision == coordinates.predecessor_revision
        and record.successor_marking_identity
        == coordinates.successor_marking_identity
        and record.successor_revision == coordinates.successor_revision
    )


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _finalize_commit_state(
    active: dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionReservation,
    ],
    current: dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionCurrentPredecessor,
    ],
    consumed: set[ExperimentalWorkflowPureActionReservationIdentity],
    commits: dict[
        ExperimentalWorkflowPureActionReservationIdentity,
        ExperimentalWorkflowPureActionCommitCoordinates,
    ],
) -> tuple[
    dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionReservation,
    ],
    dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionCurrentPredecessor,
    ],
    set[ExperimentalWorkflowPureActionReservationIdentity],
    dict[
        ExperimentalWorkflowPureActionReservationIdentity,
        ExperimentalWorkflowPureActionCommitCoordinates,
    ],
]:
    """Return staged state; assignment by the caller is the commit point."""
    return active, current, consumed, commits


def _reconstruct_reservation(
    value: ExperimentalWorkflowPureActionReservation,
) -> ExperimentalWorkflowPureActionReservation:
    if type(value) is not ExperimentalWorkflowPureActionReservation:
        raise TypeError(
            "reservation must be ExperimentalWorkflowPureActionReservation"
        )
    validated = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=value.execution_plan_identity,
        execution_bindings_identity=value.execution_bindings_identity,
        selected_binding_evidence_identity=(
            value.selected_binding_evidence_identity
        ),
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
    if validated != value:
        raise ValueError("reservation differs after validation")
    return validated


__all__ = ["ExperimentalInMemoryPureActionReservationRepository"]
