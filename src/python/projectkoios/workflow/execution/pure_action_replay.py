"""Read-only reconstruction of one durable pure-action compact commit."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowMappedActionResultIdentity,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetFiringResultIdentity,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitEventJsonCodec,
    ExperimentalWorkflowPureActionCommitReadResult,
    ExperimentalWorkflowPureActionCommitReadStatus,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationRepository,
)

from .pure_action_commit import ExperimentalWorkflowPureActionCommit
from .pure_action_firing import (
    ExperimentalWorkflowPureActionFiringOutcomeIdentity,
)
from .pure_action_invocation import (
    ExperimentalWorkflowPureActionInvocationOutcomeIdentity,
)


class ExperimentalWorkflowPureActionCommittedReplayStatus(StrEnum):
    """Closed result of read-only compact committed-event reconstruction."""

    REPLAYED = "replayed"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommittedReplayResult:
    """Expose a commit only after exact event and coordinate reconstruction."""

    status: ExperimentalWorkflowPureActionCommittedReplayStatus
    commit: ExperimentalWorkflowPureActionCommit | None
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates | None
    event_sha256: str | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.status) is not (
            ExperimentalWorkflowPureActionCommittedReplayStatus
        ):
            raise TypeError(
                "status must be "
                "ExperimentalWorkflowPureActionCommittedReplayStatus"
            )
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")
        if self.status is (
            ExperimentalWorkflowPureActionCommittedReplayStatus.REPLAYED
        ):
            if type(self.commit) is not ExperimentalWorkflowPureActionCommit:
                raise TypeError("replayed status requires a commit")
            if type(self.coordinates) is not (
                ExperimentalWorkflowPureActionCommitCoordinates
            ):
                raise TypeError("replayed status requires commit coordinates")
            if (
                type(self.event_sha256) is not str
                or len(self.event_sha256) != 64
                or self.event_sha256 != self.event_sha256.lower()
                or any(
                    character not in "0123456789abcdef"
                    for character in self.event_sha256
                )
            ):
                raise TypeError("replayed status requires event SHA-256")
            if self.diagnostics:
                raise ValueError("replayed status prohibits diagnostics")
        elif (
            self.commit is not None
            or self.coordinates is not None
            or self.event_sha256 is not None
        ):
            raise ValueError("non-replayed status prohibits retained commit")
        elif not self.diagnostics:
            raise ValueError("non-replayed status requires diagnostics")


@final
class ExperimentalWorkflowPureActionCommittedReplayService:
    """Reconstruct a compact committed event without invoking owner or CPN."""

    __slots__ = ("_repository",)

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionReservationRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionReservationRepository,
        ):
            raise TypeError(
                "repository must implement "
                "ExperimentalWorkflowPureActionReservationRepository"
            )
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCommittedReplayService "
            "is not subclassable"
        )

    def execute(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommittedReplayResult:
        """Load and reconstruct one exact compact committed event."""
        if type(reservation_identity) is not (
            ExperimentalWorkflowPureActionReservationIdentity
        ):
            raise TypeError(
                "reservation_identity must be "
                "ExperimentalWorkflowPureActionReservationIdentity"
            )
        try:
            loaded = self._repository.load_committed_snapshot(
                reservation_identity
            )
        except Exception:
            return _failure(
                ExperimentalWorkflowPureActionCommittedReplayStatus.ERROR,
                "commit_repository_error",
            )
        if type(loaded) is not ExperimentalWorkflowPureActionCommitReadResult:
            return _failure(
                ExperimentalWorkflowPureActionCommittedReplayStatus.ERROR,
                "commit_repository_invalid_result",
            )
        if (
            loaded.status
            is not ExperimentalWorkflowPureActionCommitReadStatus.FOUND
        ):
            status = {
                ExperimentalWorkflowPureActionCommitReadStatus.ABSENT: (
                    ExperimentalWorkflowPureActionCommittedReplayStatus.ABSENT
                ),
                ExperimentalWorkflowPureActionCommitReadStatus.INCOMPATIBLE: (
                    ExperimentalWorkflowPureActionCommittedReplayStatus.INCOMPATIBLE
                ),
                ExperimentalWorkflowPureActionCommitReadStatus.CORRUPT: (
                    ExperimentalWorkflowPureActionCommittedReplayStatus.CORRUPT
                ),
                ExperimentalWorkflowPureActionCommitReadStatus.ERROR: (
                    ExperimentalWorkflowPureActionCommittedReplayStatus.ERROR
                ),
            }[loaded.status]
            return _failure(status, loaded.diagnostics[0])
        assert loaded.snapshot is not None
        coordinates = loaded.snapshot.coordinates
        record = loaded.snapshot.record
        event = loaded.snapshot.event_bytes
        try:
            decoded = (
                ExperimentalWorkflowPureActionCommitEventJsonCodec().decode(
                    event
                )
            )
            if decoded != record:
                raise ValueError("commit_event_record_mismatch")
            commit = _reconstruct_commit(record)
            _validate_coordinates(commit, record, coordinates)
        except (TypeError, ValueError) as error:
            return _failure(
                ExperimentalWorkflowPureActionCommittedReplayStatus.CORRUPT,
                (str(error) or "commit_reconstruction_failed")[:128],
            )
        return ExperimentalWorkflowPureActionCommittedReplayResult(
            status=ExperimentalWorkflowPureActionCommittedReplayStatus.REPLAYED,
            commit=commit,
            coordinates=coordinates,
            event_sha256=sha256(event).hexdigest(),
            diagnostics=(),
        )


def _reconstruct_commit(
    record: ExperimentalWorkflowPureActionCommitRecord,
) -> ExperimentalWorkflowPureActionCommit:
    commit = ExperimentalWorkflowPureActionCommit(
        cpn_plan_identity=record.cpn_plan_identity,
        reservation_identity=record.reservation_identity,
        input_authorization_identity=record.input_authorization_identity,
        source_authority_identities=tuple(
            item.identity for item in record.source_authorities
        ),
        invocation_outcome_identity=ExperimentalWorkflowPureActionInvocationOutcomeIdentity(
            record.invocation_outcome_identity
        ),
        request_identity=record.request_identity,
        owner_result_identity=record.owner_result_identity,
        mapped_result_identity=ExperimentalWorkflowMappedActionResultIdentity(
            record.mapped_result_identity
        ),
        firing_outcome_identity=ExperimentalWorkflowPureActionFiringOutcomeIdentity(
            record.firing_outcome_identity
        ),
        cpn_firing_result_identity=ColoredPetriNetFiringResultIdentity(
            record.cpn_firing_result_identity
        ),
        predecessor_marking_identity=record.predecessor_marking_identity,
        predecessor_revision=record.predecessor_revision,
        successor_marking_identity=record.successor_marking_identity,
        successor_revision=record.successor_revision,
    )
    if commit.identity != record.commit_identity:
        raise ValueError("commit identity differs from canonical event")
    return commit


def _validate_coordinates(
    commit: ExperimentalWorkflowPureActionCommit,
    record: ExperimentalWorkflowPureActionCommitRecord,
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
) -> None:
    if (
        coordinates.commit_identity != commit.identity
        or coordinates.reservation_identity != commit.reservation_identity
        or coordinates.net_instance_identity != record.net_instance_identity
        or coordinates.predecessor_marking_identity
        != commit.predecessor_marking_identity
        or coordinates.predecessor_revision != commit.predecessor_revision
        or coordinates.successor_marking_identity
        != commit.successor_marking_identity
        or coordinates.successor_revision != commit.successor_revision
    ):
        raise ValueError("commit coordinates differ from canonical event")


def _failure(
    status: ExperimentalWorkflowPureActionCommittedReplayStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCommittedReplayResult:
    return ExperimentalWorkflowPureActionCommittedReplayResult(
        status=status,
        commit=None,
        coordinates=None,
        event_sha256=None,
        diagnostics=(diagnostic,),
    )


__all__ = [
    "ExperimentalWorkflowPureActionCommittedReplayResult",
    "ExperimentalWorkflowPureActionCommittedReplayService",
    "ExperimentalWorkflowPureActionCommittedReplayStatus",
]
