"""Nominal repository port for pure-action reservations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from projectkoios.workflow_sdk.identities import WorkflowNetInstanceIdentity

from ._pure_action_reservation_records import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitReadResult,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)


class ExperimentalWorkflowPureActionReservationRepository(ABC):
    """Nominal atomic boundary for current predecessor reservations."""

    __slots__ = ()

    @abstractmethod
    def reserve(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionReserveStatus:
        """Atomically reserve the exact current predecessor or fail closed."""

    @abstractmethod
    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        """Return whether the exact retained reservation remains current."""

    @abstractmethod
    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically retain a commit, consume, and advance the predecessor."""

    @abstractmethod
    def load_committed_snapshot(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitReadResult:
        """Atomically load one closed compact committed snapshot result."""

    @abstractmethod
    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load compact committed coordinates for exact replay inspection."""

    @abstractmethod
    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the complete compact commit record for replay inspection."""

    @abstractmethod
    def load_commit_event(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> bytes | None:
        """Load the exact canonical committed-event bytes."""

    @abstractmethod
    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the repository-owned current predecessor coordinate."""


__all__ = ["ExperimentalWorkflowPureActionReservationRepository"]
