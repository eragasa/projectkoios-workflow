"""Workflow transition replay."""

from __future__ import annotations

from dataclasses import dataclass

from ..identities.definition import (
    WorkflowAuditEventIdentity,
    WorkflowReplayIdentity,
    WorkflowTransitionOutcomeIdentity,
    stable_identity,
)
from ..records.contract import WORKFLOW_CORE_CONTRACT_VERSION
from .execution import WorkflowTransitionProcessor
from .inputs import WorkflowTransitionInput
from .results import WorkflowTransitionExecution


@dataclass(frozen=True, slots=True)
class WorkflowReplayResult:
    """Deterministic comparison between retained and recomputed execution."""

    identity: WorkflowReplayIdentity
    expected_outcome_identity: WorkflowTransitionOutcomeIdentity
    replayed_outcome_identity: WorkflowTransitionOutcomeIdentity
    expected_audit_identity: WorkflowAuditEventIdentity
    replayed_audit_identity: WorkflowAuditEventIdentity
    matches: bool
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        expected: WorkflowTransitionExecution,
        replayed: WorkflowTransitionExecution,
    ) -> WorkflowReplayResult:
        """Create a content-identified replay comparison."""
        matches = expected == replayed
        identity = WorkflowReplayIdentity(
            stable_identity(
                "workflow-replay-result",
                expected.outcome.identity,
                replayed.outcome.identity,
                expected.audit_event.identity,
                replayed.audit_event.identity,
                matches,
                WORKFLOW_CORE_CONTRACT_VERSION,
            )
        )
        return cls(
            identity,
            expected.outcome.identity,
            replayed.outcome.identity,
            expected.audit_event.identity,
            replayed.audit_event.identity,
            matches,
        )

    def __post_init__(self) -> None:
        if type(self.identity) is not WorkflowReplayIdentity:
            raise TypeError("identity must be WorkflowReplayIdentity")
        for name in (
            "expected_outcome_identity",
            "replayed_outcome_identity",
        ):
            if (
                type(getattr(self, name))
                is not WorkflowTransitionOutcomeIdentity
            ):
                raise TypeError(
                    f"{name} must be WorkflowTransitionOutcomeIdentity"
                )
        for name in ("expected_audit_identity", "replayed_audit_identity"):
            if type(getattr(self, name)) is not WorkflowAuditEventIdentity:
                raise TypeError(f"{name} must be WorkflowAuditEventIdentity")
        if type(self.matches) is not bool:
            raise TypeError("matches must be a Boolean")
        if self.contract_version != WORKFLOW_CORE_CONTRACT_VERSION:
            raise ValueError("unsupported workflow-core contract version")
        expected_identity = WorkflowReplayIdentity(
            stable_identity(
                "workflow-replay-result",
                self.expected_outcome_identity,
                self.replayed_outcome_identity,
                self.expected_audit_identity,
                self.replayed_audit_identity,
                self.matches,
                WORKFLOW_CORE_CONTRACT_VERSION,
            )
        )
        if self.identity != expected_identity:
            raise ValueError("replay result identity is inconsistent")


class WorkflowTransitionReplayer:
    """Pure action recomputing a prior execution from its exact inputs."""

    def execute(
        self,
        transition_input: WorkflowTransitionInput,
        expected: WorkflowTransitionExecution,
    ) -> WorkflowReplayResult:
        """Replay without effects and compare immutable objects."""
        if type(transition_input) is not WorkflowTransitionInput:
            raise TypeError("transition_input must be WorkflowTransitionInput")
        if type(expected) is not WorkflowTransitionExecution:
            raise TypeError("expected must be WorkflowTransitionExecution")
        replayed = WorkflowTransitionProcessor().execute(transition_input)
        return WorkflowReplayResult.create(expected=expected, replayed=replayed)
