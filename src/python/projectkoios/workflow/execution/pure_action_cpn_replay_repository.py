"""Nominal repository port for durable pure-CPN replay evidence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionReservation,
)

from .pure_action_cpn_replay_evidence import (
    ExperimentalWorkflowPureActionCpnReplayEvidence,
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult,
)


class ExperimentalWorkflowPureActionCpnReplayEvidenceRepository(ABC):
    """Atomically commit and read canonical replay evidence."""

    @abstractmethod
    def commit_with_cpn_replay(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord,
        evidence: ExperimentalWorkflowPureActionCpnReplayEvidence,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        raise NotImplementedError

    @abstractmethod
    def load_cpn_replay_evidence(
        self, commit_identity: ExperimentalWorkflowPureActionCommitIdentity
    ) -> ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult:
        raise NotImplementedError


__all__ = ["ExperimentalWorkflowPureActionCpnReplayEvidenceRepository"]
