"""Audits owned by the immutable Workflow core."""

from __future__ import annotations

from dataclasses import dataclass

from ..identities.definition import (
    WorkflowAdapterEvidenceIdentity,
    WorkflowArtifactReferenceIdentity,
    WorkflowAuditEventIdentity,
    WorkflowDecisionReferenceIdentity,
    WorkflowInfrastructureFailureIdentity,
    WorkflowRunIdentity,
    WorkflowTransitionOutcomeIdentity,
    WorkflowTransitionRequestIdentity,
    WorkflowValidationIdentity,
    stable_identity,
)
from .contract import (
    _MAX_STATE_REFERENCES,
    _MAX_STRING_CHARACTERS,
    WORKFLOW_CORE_CONTRACT_VERSION,
)

type WorkflowAuditReferenceIdentity = (
    WorkflowTransitionRequestIdentity
    | WorkflowTransitionOutcomeIdentity
    | WorkflowValidationIdentity
    | WorkflowAdapterEvidenceIdentity
    | WorkflowInfrastructureFailureIdentity
    | WorkflowArtifactReferenceIdentity
    | WorkflowDecisionReferenceIdentity
)
_AUDIT_REFERENCE_IDENTITY_TYPES = (
    WorkflowTransitionRequestIdentity,
    WorkflowTransitionOutcomeIdentity,
    WorkflowValidationIdentity,
    WorkflowAdapterEvidenceIdentity,
    WorkflowInfrastructureFailureIdentity,
    WorkflowArtifactReferenceIdentity,
    WorkflowDecisionReferenceIdentity,
)


@dataclass(frozen=True, slots=True)
class WorkflowAuditReference:
    """Nominal reference retained by a workflow audit event."""

    reference_identity: WorkflowAuditReferenceIdentity

    def __post_init__(self) -> None:
        if type(self.reference_identity) not in _AUDIT_REFERENCE_IDENTITY_TYPES:
            raise TypeError("unsupported workflow audit reference identity")

    def identity_parts(self) -> tuple[object, ...]:
        """Return the nominal identity without erasing its runtime type."""
        return (self.reference_identity,)


@dataclass(frozen=True, slots=True)
class WorkflowAuditEvent:
    """Bounded immutable observation about transition processing."""

    identity: WorkflowAuditEventIdentity
    run_identity: WorkflowRunIdentity
    sequence_revision: int
    attempt_identity: WorkflowTransitionRequestIdentity
    event_kind: str
    subject_references: tuple[WorkflowAuditReference, ...]
    evidence_references: tuple[WorkflowAuditReference, ...]
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        run_identity: WorkflowRunIdentity,
        sequence_revision: int,
        attempt_identity: WorkflowTransitionRequestIdentity,
        event_kind: str,
        subject_references: tuple[WorkflowAuditReference, ...],
        evidence_references: tuple[WorkflowAuditReference, ...],
    ) -> WorkflowAuditEvent:
        """Create a deterministic audit event without persistence or a clock."""
        identity = _audit_event_identity(
            run_identity,
            sequence_revision,
            attempt_identity,
            event_kind,
            subject_references,
            evidence_references,
        )
        return cls(
            identity,
            run_identity,
            sequence_revision,
            attempt_identity,
            event_kind,
            subject_references,
            evidence_references,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "audit event identity", self.identity, WorkflowAuditEventIdentity
        )
        _exact_type("run identity", self.run_identity, WorkflowRunIdentity)
        _nonnegative_integer("audit sequence revision", self.sequence_revision)
        _exact_type(
            "audit attempt identity",
            self.attempt_identity,
            WorkflowTransitionRequestIdentity,
        )
        _bounded_string("audit event kind", self.event_kind)
        _audit_references(
            "audit subject references",
            self.subject_references,
            allow_empty=False,
        )
        _audit_references(
            "audit evidence references",
            self.evidence_references,
            allow_empty=True,
        )
        if self.identity != _audit_event_identity(
            self.run_identity,
            self.sequence_revision,
            self.attempt_identity,
            self.event_kind,
            self.subject_references,
            self.evidence_references,
        ):
            raise ValueError("audit event identity is inconsistent")


def _audit_event_identity(
    run_identity: WorkflowRunIdentity,
    revision: int,
    attempt_identity: WorkflowTransitionRequestIdentity,
    event_kind: str,
    subject_references: tuple[WorkflowAuditReference, ...],
    evidence_references: tuple[WorkflowAuditReference, ...],
) -> WorkflowAuditEventIdentity:
    return WorkflowAuditEventIdentity(
        stable_identity(
            "workflow-audit-event",
            run_identity,
            revision,
            attempt_identity,
            event_kind,
            tuple(item.identity_parts() for item in subject_references),
            tuple(item.identity_parts() for item in evidence_references),
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _contract_version(value: str) -> None:
    if value != WORKFLOW_CORE_CONTRACT_VERSION:
        raise ValueError("unsupported workflow-core contract version")


def _exact_type(name: str, value: object, expected: type) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be {expected.__name__}")


def _bounded_string(
    name: str,
    value: str,
    *,
    maximum: int = _MAX_STRING_CHARACTERS,
) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if not value or len(value) > maximum:
        raise ValueError(f"{name} must be nonempty and bounded")


def _audit_references(
    name: str,
    values: tuple[WorkflowAuditReference, ...],
    *,
    allow_empty: bool,
) -> None:
    if type(values) is not tuple or any(
        type(item) is not WorkflowAuditReference for item in values
    ):
        raise TypeError(f"{name} must be a WorkflowAuditReference tuple")
    if not allow_empty and not values:
        raise ValueError(f"{name} must not be empty")
    if len(values) > _MAX_STATE_REFERENCES:
        raise ValueError(f"{name} contains too many items")


def _nonnegative_integer(name: str, value: int) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
