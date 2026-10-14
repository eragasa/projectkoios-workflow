"""Kinds owned by the immutable Workflow core."""

from __future__ import annotations

from enum import StrEnum


class WorkflowRunStatus(StrEnum):
    """Operational lifecycle state, distinct from domain acceptance."""

    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """Return whether no later transition may be applied to this run."""
        return self in {
            WorkflowRunStatus.COMPLETED,
            WorkflowRunStatus.FAILED,
            WorkflowRunStatus.CANCELLED,
        }


class WorkflowArtifactDisposition(StrEnum):
    """Operational origin, never scientific or publication acceptance."""

    OBSERVED = "observed"
    GENERATED_UNREVIEWED = "generated_unreviewed"


class WorkflowAdapterDisposition(StrEnum):
    """Engine-adapter determination for one validated request."""

    ENABLED = "enabled"
    NOT_ENABLED = "not_enabled"
    BLOCKED = "blocked"


class WorkflowTransitionOutcomeKind(StrEnum):
    """Closed core outcomes for transition processing."""

    APPLIED = "applied"
    REJECTED_INVALID = "rejected_invalid"
    NOT_ENABLED = "not_enabled"
    CONFLICT = "conflict"
    BLOCKED = "blocked"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"


class WorkflowValidationFindingCode(StrEnum):
    """Stable categories for cross-record workflow validation findings."""

    DEFINITION_MISMATCH = "definition_mismatch"
    RUN_MISMATCH = "run_mismatch"
    STATE_MISMATCH = "state_mismatch"
    REVISION_CONFLICT = "revision_conflict"
    TERMINAL_RUN = "terminal_run"
    UNKNOWN_OPERATION = "unknown_operation"
    AUTHORITY_SUBJECT_MISMATCH = "authority_subject_mismatch"
    AUTHORITY_SCOPE_MISMATCH = "authority_scope_mismatch"
    ADAPTER_EVIDENCE_MISMATCH = "adapter_evidence_mismatch"
    ADAPTER_OUTPUT_INVALID = "adapter_output_invalid"
    INFRASTRUCTURE_EVIDENCE_MISMATCH = "infrastructure_evidence_mismatch"
    DUPLICATE_REFERENCE = "duplicate_reference"
    FINDINGS_TRUNCATED = "findings_truncated"
