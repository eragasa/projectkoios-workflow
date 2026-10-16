"""Bounded structural reconstruction of committed pure-action safety state."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import final

from projectkoios.workflow.petrinet.colored import ColoredPetriNetMarking
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommittedSnapshot,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationLifecycleEvent,
    ExperimentalWorkflowPureActionReservationLifecycleState,
)

from .pure_action_cpn_replay_evidence import (
    ExperimentalWorkflowPureActionCpnReplayEvidence,
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionSafetyStateSnapshot:
    """One correlated committed state without owner-controlled payloads."""

    initial_predecessor: ExperimentalWorkflowPureActionCurrentPredecessor
    current_predecessor: ExperimentalWorkflowPureActionCurrentPredecessor
    lifecycle: tuple[
        ExperimentalWorkflowPureActionReservationLifecycleEvent, ...
    ]
    committed_snapshot: ExperimentalWorkflowPureActionCommittedSnapshot
    replay_evidence: ExperimentalWorkflowPureActionCpnReplayEvidence
    predecessor_marking: ColoredPetriNetMarking
    successor_marking: ColoredPetriNetMarking

    def __post_init__(self) -> None:
        if (
            type(self.initial_predecessor)
            is not ExperimentalWorkflowPureActionCurrentPredecessor
        ):
            raise TypeError(
                "initial_predecessor must be current-predecessor record"
            )
        if (
            type(self.current_predecessor)
            is not ExperimentalWorkflowPureActionCurrentPredecessor
        ):
            raise TypeError(
                "current_predecessor must be current-predecessor record"
            )
        if type(self.lifecycle) is not tuple or len(self.lifecycle) != 2:
            raise ValueError(
                "committed safety state requires two lifecycle events"
            )
        if any(
            type(event)
            is not ExperimentalWorkflowPureActionReservationLifecycleEvent
            for event in self.lifecycle
        ):
            raise TypeError("lifecycle must contain lifecycle events")
        if (
            type(self.committed_snapshot)
            is not ExperimentalWorkflowPureActionCommittedSnapshot
        ):
            raise TypeError("committed_snapshot must be committed snapshot")
        if (
            type(self.replay_evidence)
            is not ExperimentalWorkflowPureActionCpnReplayEvidence
        ):
            raise TypeError("replay_evidence must be CPN replay evidence")
        if (
            type(self.predecessor_marking) is not ColoredPetriNetMarking
            or type(self.successor_marking) is not ColoredPetriNetMarking
        ):
            raise TypeError("markings must be ColoredPetriNetMarking")
        record = self.committed_snapshot.record
        reservation = self.lifecycle[0].reservation
        lifecycle_state = (
            ExperimentalWorkflowPureActionReservationLifecycleState
        )
        if (
            self.initial_predecessor.net_instance_identity
            != record.net_instance_identity
            or self.current_predecessor.net_instance_identity
            != record.net_instance_identity
            or self.lifecycle[0].state is not lifecycle_state.RESERVED
            or self.lifecycle[1].state is not lifecycle_state.COMMITTED
            or any(event.reservation != reservation for event in self.lifecycle)
            or self.lifecycle[1].commit_identity != record.commit_identity
            or reservation.identity != record.reservation_identity
            or reservation.cpn_plan_identity != record.cpn_plan_identity
            or reservation.input_authorization_identity
            != record.input_authorization_identity
            or reservation.request_identity != record.request_identity
            or reservation.net_instance_identity != record.net_instance_identity
            or reservation.predecessor_marking_identity
            != record.predecessor_marking_identity
            or reservation.predecessor_revision != record.predecessor_revision
            or self.replay_evidence.commit_identity != record.commit_identity
            or self.replay_evidence.cpn_plan_identity
            != record.cpn_plan_identity
            or self.replay_evidence.cpn_firing_result_identity
            != record.cpn_firing_result_identity
            or self.predecessor_marking.identity.value
            != record.predecessor_marking_identity.value
            or self.successor_marking.identity.value
            != record.successor_marking_identity.value
        ):
            raise ValueError("safety-state components are not correlated")


class ExperimentalWorkflowPureActionSafetyStateReadStatus(StrEnum):
    FOUND = "found"
    LEGACY_PARTIAL = "legacy_partial"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionSafetyStateReadResult:
    status: ExperimentalWorkflowPureActionSafetyStateReadStatus
    snapshot: ExperimentalWorkflowPureActionSafetyStateSnapshot | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionSafetyStateReadStatus
        ):
            raise TypeError("status must be safety-state read status")
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")
        if (
            self.status
            is ExperimentalWorkflowPureActionSafetyStateReadStatus.FOUND
        ):
            if (
                type(self.snapshot)
                is not ExperimentalWorkflowPureActionSafetyStateSnapshot
            ):
                raise TypeError("found safety state requires snapshot")
            if self.diagnostics:
                raise ValueError("found safety state prohibits diagnostics")
        elif self.snapshot is not None or not self.diagnostics:
            raise ValueError("non-found safety state requires diagnostics")


class ExperimentalWorkflowPureActionSafetyStateRepository(ABC):
    @abstractmethod
    def load_committed_safety_state(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionSafetyStateReadResult:
        raise NotImplementedError


@final
class ExperimentalWorkflowPureActionSafetyStateReplayService:
    """Read bounded committed state without executing integrations or CPNs."""

    __slots__ = ("_repository",)

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionSafetyStateRepository,
    ) -> None:
        if not isinstance(
            repository, ExperimentalWorkflowPureActionSafetyStateRepository
        ):
            raise TypeError("repository must implement safety-state repository")
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError("safety-state replay service is not subclassable")

    def execute(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionSafetyStateReadResult:
        return self._repository.load_committed_safety_state(
            reservation_identity
        )


__all__ = [
    "ExperimentalWorkflowPureActionSafetyStateReadResult",
    "ExperimentalWorkflowPureActionSafetyStateReadStatus",
    "ExperimentalWorkflowPureActionSafetyStateReplayService",
    "ExperimentalWorkflowPureActionSafetyStateRepository",
    "ExperimentalWorkflowPureActionSafetyStateSnapshot",
]
