"""Workflow transition results."""

from __future__ import annotations

from dataclasses import dataclass

from ..records.audits import WorkflowAuditEvent, WorkflowAuditReference
from ..records.outcomes import WorkflowTransitionOutcome


@dataclass(frozen=True, slots=True)
class WorkflowTransitionExecution:
    """Pure transition outcome and its immutable audit event."""

    outcome: WorkflowTransitionOutcome
    audit_event: WorkflowAuditEvent

    def __post_init__(self) -> None:
        if type(self.outcome) is not WorkflowTransitionOutcome:
            raise TypeError("outcome must be WorkflowTransitionOutcome")
        if type(self.audit_event) is not WorkflowAuditEvent:
            raise TypeError("audit_event must be WorkflowAuditEvent")
        expected_subjects = (
            WorkflowAuditReference(self.outcome.request_identity),
            WorkflowAuditReference(self.outcome.identity),
        )
        expected_evidence = [
            WorkflowAuditReference(self.outcome.validation.identity)
        ]
        if self.outcome.adapter_evidence_identity is not None:
            expected_evidence.append(
                WorkflowAuditReference(self.outcome.adapter_evidence_identity)
            )
        if self.outcome.infrastructure_failure_identity is not None:
            expected_evidence.append(
                WorkflowAuditReference(
                    self.outcome.infrastructure_failure_identity
                )
            )
        expected_revision = (
            self.outcome.successor_run.revision
            if self.outcome.successor_run is not None
            else self.outcome.prior_revision
        )
        if (
            self.audit_event.run_identity != self.outcome.run_identity
            or self.audit_event.sequence_revision != expected_revision
            or self.audit_event.attempt_identity
            != self.outcome.request_identity
            or self.audit_event.event_kind
            != f"transition.{self.outcome.kind.value}"
            or self.audit_event.subject_references != expected_subjects
            or self.audit_event.evidence_references != tuple(expected_evidence)
        ):
            raise ValueError("audit event is inconsistent with its outcome")
