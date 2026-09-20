"""Immutable Petri-independent workflow-core records.

The records in this module carry bounded state and references only. They perform
no persistence, dispatch, external execution, scientific calculation, or human
decision. Construction validates intrinsic invariants; cross-record validation
belongs to :mod:`projectkoios.workflow.core.processing`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from .identities import (
    WorkflowActorIdentity,
    WorkflowAdapterEvidenceIdentity,
    WorkflowAdapterIdentity,
    WorkflowArtifactReferenceIdentity,
    WorkflowAuditEventIdentity,
    WorkflowAuthorityReferenceIdentity,
    WorkflowDecisionReferenceIdentity,
    WorkflowDefinitionIdentity,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowInfrastructureFailureIdentity,
    WorkflowOperationIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    WorkflowSubjectIdentity,
    WorkflowTransitionOutcomeIdentity,
    WorkflowTransitionRequestIdentity,
    WorkflowValidationFindingIdentity,
    WorkflowValidationIdentity,
    stable_identity,
)

WORKFLOW_CORE_CONTRACT_VERSION = "0.1.0"
_MAX_STRING_CHARACTERS = 4_096
_MAX_MESSAGE_CHARACTERS = 65_536
_MAX_OPERATIONS = 256
_MAX_STATE_REFERENCES = 4_096
_MAX_INPUT_REFERENCES = 4_096
_MAX_ARTIFACT_REFERENCES = 4_096
_MAX_DECISION_REFERENCES = 1_024
_MAX_REASONS = 256
_MAX_FINDINGS = 1_024
_SHA256_CHARACTERS = frozenset("0123456789abcdef")


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
class WorkflowTypedReference:
    """Bounded opaque reference to adapter- or application-owned state."""

    reference_kind: str
    reference_identity: WorkflowExternalReferenceIdentity
    digest_sha256: str | None = None

    def __post_init__(self) -> None:
        _bounded_string("reference kind", self.reference_kind)
        _exact_type(
            "reference identity",
            self.reference_identity,
            WorkflowExternalReferenceIdentity,
        )
        if self.digest_sha256 is not None:
            _sha256("reference digest", self.digest_sha256)

    def identity_parts(self) -> tuple[object, ...]:
        """Return exact semantic fields used by containing identities."""
        return (
            self.reference_kind,
            self.reference_identity,
            self.digest_sha256,
        )


@dataclass(frozen=True, slots=True)
class WorkflowArtifactReference:
    """Typed immutable reference to an externally owned artifact payload."""

    identity: WorkflowArtifactReferenceIdentity
    artifact_identity: WorkflowExternalReferenceIdentity
    artifact_kind: str
    digest_sha256: str
    role: str
    disposition: WorkflowArtifactDisposition
    provenance_identity: WorkflowExternalReferenceIdentity
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        artifact_identity: WorkflowExternalReferenceIdentity,
        artifact_kind: str,
        digest_sha256: str,
        role: str,
        disposition: WorkflowArtifactDisposition,
        provenance_identity: WorkflowExternalReferenceIdentity,
    ) -> WorkflowArtifactReference:
        """Create one content-identified artifact reference without I/O."""
        identity = _artifact_reference_identity(
            artifact_identity,
            artifact_kind,
            digest_sha256,
            role,
            disposition,
            provenance_identity,
        )
        return cls(
            identity,
            artifact_identity,
            artifact_kind,
            digest_sha256,
            role,
            disposition,
            provenance_identity,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "artifact reference identity",
            self.identity,
            WorkflowArtifactReferenceIdentity,
        )
        _exact_type(
            "artifact identity",
            self.artifact_identity,
            WorkflowExternalReferenceIdentity,
        )
        _bounded_string("artifact kind", self.artifact_kind)
        _sha256("artifact digest", self.digest_sha256)
        _bounded_string("artifact role", self.role)
        if not isinstance(self.disposition, WorkflowArtifactDisposition):
            raise TypeError("disposition must be WorkflowArtifactDisposition")
        _exact_type(
            "provenance identity",
            self.provenance_identity,
            WorkflowExternalReferenceIdentity,
        )
        if self.identity != _artifact_reference_identity(
            self.artifact_identity,
            self.artifact_kind,
            self.digest_sha256,
            self.role,
            self.disposition,
            self.provenance_identity,
        ):
            raise ValueError("artifact reference identity is inconsistent")

    def identity_parts(self) -> tuple[object, ...]:
        """Return the complete immutable artifact-reference identity."""
        return (
            self.identity,
            self.artifact_identity,
            self.artifact_kind,
            self.digest_sha256,
            self.role,
            self.disposition,
            self.provenance_identity,
        )


@dataclass(frozen=True, slots=True)
class WorkflowAuthorityReference:
    """Reference to externally owned bounded authority evidence."""

    identity: WorkflowAuthorityReferenceIdentity
    authority_kind: str
    subject_identity: WorkflowSubjectIdentity
    operation_identities: tuple[WorkflowOperationIdentity, ...]
    evidence_identity: WorkflowExternalReferenceIdentity
    authority_version: str
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        authority_kind: str,
        subject_identity: WorkflowSubjectIdentity,
        operation_identities: tuple[WorkflowOperationIdentity, ...],
        evidence_identity: WorkflowExternalReferenceIdentity,
        authority_version: str,
    ) -> WorkflowAuthorityReference:
        """Create one scoped authority reference without granting authority."""
        operations = _canonical_operation_identities(
            "authority operations",
            operation_identities,
            _MAX_OPERATIONS,
        )
        identity = _authority_reference_identity(
            authority_kind,
            subject_identity,
            operations,
            evidence_identity,
            authority_version,
        )
        return cls(
            identity,
            authority_kind,
            subject_identity,
            operations,
            evidence_identity,
            authority_version,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "authority reference identity",
            self.identity,
            WorkflowAuthorityReferenceIdentity,
        )
        _bounded_string("authority kind", self.authority_kind)
        _exact_type(
            "authority subject identity",
            self.subject_identity,
            WorkflowSubjectIdentity,
        )
        operations = _canonical_operation_identities(
            "authority operations",
            self.operation_identities,
            _MAX_OPERATIONS,
        )
        if operations != self.operation_identities:
            raise ValueError("authority operations must be canonically ordered")
        _exact_type(
            "authority evidence identity",
            self.evidence_identity,
            WorkflowExternalReferenceIdentity,
        )
        _bounded_string("authority version", self.authority_version)
        if self.identity != _authority_reference_identity(
            self.authority_kind,
            self.subject_identity,
            self.operation_identities,
            self.evidence_identity,
            self.authority_version,
        ):
            raise ValueError("authority reference identity is inconsistent")


@dataclass(frozen=True, slots=True)
class WorkflowDecisionReference:
    """Reference to a separate human, technical, or lifecycle decision."""

    identity: WorkflowDecisionReferenceIdentity
    decision_kind: str
    scope: str
    subject_identity: WorkflowSubjectIdentity
    authority_identity: WorkflowExternalReferenceIdentity
    outcome: str
    evidence_identity: WorkflowExternalReferenceIdentity
    decision_version: str
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        decision_kind: str,
        scope: str,
        subject_identity: WorkflowSubjectIdentity,
        authority_identity: WorkflowExternalReferenceIdentity,
        outcome: str,
        evidence_identity: WorkflowExternalReferenceIdentity,
        decision_version: str,
    ) -> WorkflowDecisionReference:
        """Create a content-identified decision reference without deciding."""
        identity = _decision_reference_identity(
            decision_kind,
            scope,
            subject_identity,
            authority_identity,
            outcome,
            evidence_identity,
            decision_version,
        )
        return cls(
            identity,
            decision_kind,
            scope,
            subject_identity,
            authority_identity,
            outcome,
            evidence_identity,
            decision_version,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "decision reference identity",
            self.identity,
            WorkflowDecisionReferenceIdentity,
        )
        for name in ("decision_kind", "scope", "outcome", "decision_version"):
            _bounded_string(name.replace("_", " "), getattr(self, name))
        _exact_type(
            "decision subject identity",
            self.subject_identity,
            WorkflowSubjectIdentity,
        )
        _exact_type(
            "decision authority identity",
            self.authority_identity,
            WorkflowExternalReferenceIdentity,
        )
        _exact_type(
            "decision evidence identity",
            self.evidence_identity,
            WorkflowExternalReferenceIdentity,
        )
        if self.identity != _decision_reference_identity(
            self.decision_kind,
            self.scope,
            self.subject_identity,
            self.authority_identity,
            self.outcome,
            self.evidence_identity,
            self.decision_version,
        ):
            raise ValueError("decision reference identity is inconsistent")

    def identity_parts(self) -> tuple[object, ...]:
        """Return the complete immutable decision-reference identity."""
        return (
            self.identity,
            self.decision_kind,
            self.scope,
            self.subject_identity,
            self.authority_identity,
            self.outcome,
            self.evidence_identity,
            self.decision_version,
        )


@dataclass(frozen=True, slots=True)
class WorkflowDefinitionReference:
    """Immutable reference to an engine-neutral workflow definition."""

    identity: WorkflowDefinitionIdentity
    contract_id: str
    definition_version: str
    definition_digest_sha256: str
    operation_identities: tuple[WorkflowOperationIdentity, ...]
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        contract_id: str,
        definition_version: str,
        definition_digest_sha256: str,
        operation_identities: tuple[WorkflowOperationIdentity, ...],
    ) -> WorkflowDefinitionReference:
        """Create an immutable definition reference with no executable."""
        operations = _canonical_operation_identities(
            "definition operations",
            operation_identities,
            _MAX_OPERATIONS,
        )
        identity = _definition_reference_identity(
            contract_id,
            definition_version,
            definition_digest_sha256,
            operations,
        )
        return cls(
            identity,
            contract_id,
            definition_version,
            definition_digest_sha256,
            operations,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "definition identity", self.identity, WorkflowDefinitionIdentity
        )
        _bounded_string("definition contract ID", self.contract_id)
        _bounded_string("definition version", self.definition_version)
        _sha256("definition digest", self.definition_digest_sha256)
        operations = _canonical_operation_identities(
            "definition operations",
            self.operation_identities,
            _MAX_OPERATIONS,
        )
        if operations != self.operation_identities:
            raise ValueError(
                "definition operations must be canonically ordered"
            )
        if self.identity != _definition_reference_identity(
            self.contract_id,
            self.definition_version,
            self.definition_digest_sha256,
            self.operation_identities,
        ):
            raise ValueError("definition reference identity is inconsistent")


@dataclass(frozen=True, slots=True)
class WorkflowStateSnapshot:
    """Immutable engine-neutral state for one exact run revision."""

    identity: WorkflowStateIdentity
    run_identity: WorkflowRunIdentity
    definition_identity: WorkflowDefinitionIdentity
    revision: int
    run_status: WorkflowRunStatus
    state_references: tuple[WorkflowTypedReference, ...]
    predecessor_state_identity: WorkflowStateIdentity | None
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        run_identity: WorkflowRunIdentity,
        definition_identity: WorkflowDefinitionIdentity,
        revision: int,
        run_status: WorkflowRunStatus,
        state_references: tuple[WorkflowTypedReference, ...],
        predecessor_state_identity: WorkflowStateIdentity | None,
    ) -> WorkflowStateSnapshot:
        """Create a content-identified state snapshot without persistence."""
        references = _canonical_references(state_references)
        identity = _state_snapshot_identity(
            run_identity,
            definition_identity,
            revision,
            run_status,
            references,
            predecessor_state_identity,
        )
        return cls(
            identity,
            run_identity,
            definition_identity,
            revision,
            run_status,
            references,
            predecessor_state_identity,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type("state identity", self.identity, WorkflowStateIdentity)
        _exact_type("run identity", self.run_identity, WorkflowRunIdentity)
        _exact_type(
            "definition identity",
            self.definition_identity,
            WorkflowDefinitionIdentity,
        )
        _nonnegative_integer("state revision", self.revision)
        if not isinstance(self.run_status, WorkflowRunStatus):
            raise TypeError("run_status must be WorkflowRunStatus")
        references = _canonical_references(self.state_references)
        if references != self.state_references:
            raise ValueError("state references must be canonically ordered")
        if self.predecessor_state_identity is not None:
            _exact_type(
                "predecessor state identity",
                self.predecessor_state_identity,
                WorkflowStateIdentity,
            )
        if self.revision == 0 and self.predecessor_state_identity is not None:
            raise ValueError("initial state cannot have a predecessor")
        if self.revision > 0 and self.predecessor_state_identity is None:
            raise ValueError("noninitial state must have a predecessor")
        if self.identity != _state_snapshot_identity(
            self.run_identity,
            self.definition_identity,
            self.revision,
            self.run_status,
            self.state_references,
            self.predecessor_state_identity,
        ):
            raise ValueError("state snapshot identity is inconsistent")


@dataclass(frozen=True, slots=True)
class WorkflowRun:
    """Immutable current aggregate for one identified workflow attempt."""

    MAX_ARTIFACT_REFERENCES: ClassVar[int] = _MAX_ARTIFACT_REFERENCES
    MAX_DECISION_REFERENCES: ClassVar[int] = _MAX_DECISION_REFERENCES

    identity: WorkflowRunIdentity
    run_key: str
    definition_identity: WorkflowDefinitionIdentity
    subject_identity: WorkflowSubjectIdentity
    current_state_identity: WorkflowStateIdentity
    revision: int
    status: WorkflowRunStatus
    status_reasons: tuple[str, ...] = ()
    artifact_references: tuple[WorkflowArtifactReference, ...] = ()
    decision_references: tuple[WorkflowDecisionReference, ...] = ()
    parent_run_identity: WorkflowRunIdentity | None = None
    predecessor_run_identity: WorkflowRunIdentity | None = None
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type("run identity", self.identity, WorkflowRunIdentity)
        _bounded_string("run key", self.run_key)
        _exact_type(
            "definition identity",
            self.definition_identity,
            WorkflowDefinitionIdentity,
        )
        _exact_type(
            "subject identity", self.subject_identity, WorkflowSubjectIdentity
        )
        _exact_type(
            "current state identity",
            self.current_state_identity,
            WorkflowStateIdentity,
        )
        _nonnegative_integer("run revision", self.revision)
        if not isinstance(self.status, WorkflowRunStatus):
            raise TypeError("status must be WorkflowRunStatus")
        _validate_reasons(self.status_reasons)
        if (self.status is WorkflowRunStatus.ACTIVE) != (
            not self.status_reasons
        ):
            raise ValueError(
                "active status requires no reasons; nonactive status "
                "requires reasons"
            )
        if _canonical_artifacts(self.artifact_references) != (
            self.artifact_references
        ):
            raise ValueError("run artifact references must be canonical")
        if _canonical_decisions(self.decision_references) != (
            self.decision_references
        ):
            raise ValueError("run decision references must be canonical")
        if any(
            item.subject_identity != self.subject_identity
            for item in self.decision_references
        ):
            raise ValueError("run decisions must apply to the run subject")
        for name in ("parent_run_identity", "predecessor_run_identity"):
            value = getattr(self, name)
            if value is not None:
                _exact_type(name.replace("_", " "), value, WorkflowRunIdentity)
        expected = _run_identity(
            self.run_key,
            self.definition_identity,
            self.subject_identity,
            self.parent_run_identity,
            self.predecessor_run_identity,
        )
        if self.identity != expected:
            raise ValueError("workflow run identity is inconsistent")

    def snapshot_parts(self) -> tuple[object, ...]:
        """Return all aggregate fields required for immutable evidence."""
        return (
            self.identity,
            self.run_key,
            self.definition_identity,
            self.subject_identity,
            self.current_state_identity,
            self.revision,
            self.status,
            self.status_reasons,
            tuple(item.identity_parts() for item in self.artifact_references),
            tuple(item.identity_parts() for item in self.decision_references),
            self.parent_run_identity,
            self.predecessor_run_identity,
        )


@dataclass(frozen=True, slots=True)
class WorkflowRunStartResult:
    """Pure result of starting one workflow run."""

    run: WorkflowRun
    state: WorkflowStateSnapshot

    def __post_init__(self) -> None:
        _exact_type("run", self.run, WorkflowRun)
        _exact_type("state", self.state, WorkflowStateSnapshot)
        if (
            self.run.current_state_identity != self.state.identity
            or self.run.identity != self.state.run_identity
            or self.run.definition_identity != self.state.definition_identity
            or self.run.revision != self.state.revision
            or self.run.status != self.state.run_status
        ):
            raise ValueError("started run and state must agree")


class WorkflowRunStarter:
    """Pure action that creates a new run and revision-zero state."""

    def execute(
        self,
        *,
        definition: WorkflowDefinitionReference,
        subject_identity: WorkflowSubjectIdentity,
        run_key: str,
        initial_state_references: tuple[WorkflowTypedReference, ...] = (),
        artifact_references: tuple[WorkflowArtifactReference, ...] = (),
        decision_references: tuple[WorkflowDecisionReference, ...] = (),
        parent_run_identity: WorkflowRunIdentity | None = None,
        predecessor_run_identity: WorkflowRunIdentity | None = None,
    ) -> WorkflowRunStartResult:
        """Create immutable initial state without mutation or I/O."""
        _exact_type("definition", definition, WorkflowDefinitionReference)
        _exact_type(
            "subject identity", subject_identity, WorkflowSubjectIdentity
        )
        _bounded_string("run key", run_key)
        artifacts = _canonical_artifacts(artifact_references)
        decisions = _canonical_decisions(decision_references)
        run_identity = _run_identity(
            run_key,
            definition.identity,
            subject_identity,
            parent_run_identity,
            predecessor_run_identity,
        )
        state = WorkflowStateSnapshot.create(
            run_identity=run_identity,
            definition_identity=definition.identity,
            revision=0,
            run_status=WorkflowRunStatus.ACTIVE,
            state_references=initial_state_references,
            predecessor_state_identity=None,
        )
        run = WorkflowRun(
            identity=run_identity,
            run_key=run_key,
            definition_identity=definition.identity,
            subject_identity=subject_identity,
            current_state_identity=state.identity,
            revision=0,
            status=WorkflowRunStatus.ACTIVE,
            status_reasons=(),
            artifact_references=artifacts,
            decision_references=decisions,
            parent_run_identity=parent_run_identity,
            predecessor_run_identity=predecessor_run_identity,
        )
        return WorkflowRunStartResult(run, state)


@dataclass(frozen=True, slots=True)
class WorkflowRequestBounds:
    """Request-owned limits bounded by workflow-core implementation maxima."""

    max_input_references: int = 256
    max_artifact_references: int = 256
    max_decision_references: int = 64
    max_successor_state_references: int = 1_024

    def __post_init__(self) -> None:
        for name, maximum in (
            ("max_input_references", _MAX_INPUT_REFERENCES),
            ("max_artifact_references", _MAX_ARTIFACT_REFERENCES),
            ("max_decision_references", _MAX_DECISION_REFERENCES),
            ("max_successor_state_references", _MAX_STATE_REFERENCES),
        ):
            value = getattr(self, name)
            _positive_integer(name, value)
            if value > maximum:
                raise ValueError(f"{name} exceeds its implementation maximum")

    def identity_parts(self) -> tuple[object, ...]:
        """Return all request limits in fixed semantic order."""
        return (
            self.max_input_references,
            self.max_artifact_references,
            self.max_decision_references,
            self.max_successor_state_references,
        )


@dataclass(frozen=True, slots=True)
class WorkflowTransitionRequest:
    """Immutable request for one revision-bound workflow state change."""

    identity: WorkflowTransitionRequestIdentity
    run_identity: WorkflowRunIdentity
    expected_prior_state_identity: WorkflowStateIdentity
    expected_revision: int
    operation_identity: WorkflowOperationIdentity
    input_references: tuple[WorkflowTypedReference, ...]
    artifact_references: tuple[WorkflowArtifactReference, ...]
    decision_references: tuple[WorkflowDecisionReference, ...]
    actor_identity: WorkflowActorIdentity
    authority_reference: WorkflowAuthorityReference
    idempotency_identity: WorkflowIdempotencyIdentity
    bounds: WorkflowRequestBounds
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        run_identity: WorkflowRunIdentity,
        expected_prior_state_identity: WorkflowStateIdentity,
        expected_revision: int,
        operation_identity: WorkflowOperationIdentity,
        input_references: tuple[WorkflowTypedReference, ...],
        artifact_references: tuple[WorkflowArtifactReference, ...],
        decision_references: tuple[WorkflowDecisionReference, ...],
        actor_identity: WorkflowActorIdentity,
        authority_reference: WorkflowAuthorityReference,
        idempotency_identity: WorkflowIdempotencyIdentity,
        bounds: WorkflowRequestBounds | None = None,
    ) -> WorkflowTransitionRequest:
        """Create a bounded request without authorizing it."""
        selected_bounds = bounds or WorkflowRequestBounds()
        _validate_request_collections(
            input_references,
            artifact_references,
            decision_references,
            selected_bounds,
        )
        identity = _transition_request_identity(
            run_identity,
            expected_prior_state_identity,
            expected_revision,
            operation_identity,
            input_references,
            artifact_references,
            decision_references,
            actor_identity,
            authority_reference,
            idempotency_identity,
            selected_bounds,
        )
        return cls(
            identity,
            run_identity,
            expected_prior_state_identity,
            expected_revision,
            operation_identity,
            input_references,
            artifact_references,
            decision_references,
            actor_identity,
            authority_reference,
            idempotency_identity,
            selected_bounds,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "request identity",
            self.identity,
            WorkflowTransitionRequestIdentity,
        )
        _exact_type("run identity", self.run_identity, WorkflowRunIdentity)
        _exact_type(
            "expected prior state identity",
            self.expected_prior_state_identity,
            WorkflowStateIdentity,
        )
        _nonnegative_integer("expected revision", self.expected_revision)
        _exact_type(
            "operation identity",
            self.operation_identity,
            WorkflowOperationIdentity,
        )
        _exact_type(
            "actor identity", self.actor_identity, WorkflowActorIdentity
        )
        _exact_type(
            "authority reference",
            self.authority_reference,
            WorkflowAuthorityReference,
        )
        _exact_type(
            "idempotency identity",
            self.idempotency_identity,
            WorkflowIdempotencyIdentity,
        )
        _exact_type("bounds", self.bounds, WorkflowRequestBounds)
        _validate_request_collections(
            self.input_references,
            self.artifact_references,
            self.decision_references,
            self.bounds,
        )
        if self.identity != _transition_request_identity(
            self.run_identity,
            self.expected_prior_state_identity,
            self.expected_revision,
            self.operation_identity,
            self.input_references,
            self.artifact_references,
            self.decision_references,
            self.actor_identity,
            self.authority_reference,
            self.idempotency_identity,
            self.bounds,
        ):
            raise ValueError("transition request identity is inconsistent")


@dataclass(frozen=True, slots=True)
class WorkflowAdapterEvidence:
    """Bounded engine-adapter evidence supplied to pure core processing."""

    identity: WorkflowAdapterEvidenceIdentity
    adapter_identity: WorkflowAdapterIdentity
    definition_identity: WorkflowDefinitionIdentity
    request_identity: WorkflowTransitionRequestIdentity
    prior_state_identity: WorkflowStateIdentity
    disposition: WorkflowAdapterDisposition
    successor_state_references: tuple[WorkflowTypedReference, ...] = ()
    successor_run_status: WorkflowRunStatus | None = None
    produced_artifact_references: tuple[WorkflowArtifactReference, ...] = ()
    recorded_decision_references: tuple[WorkflowDecisionReference, ...] = ()
    reasons: tuple[str, ...] = ()
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        adapter_identity: WorkflowAdapterIdentity,
        definition_identity: WorkflowDefinitionIdentity,
        request_identity: WorkflowTransitionRequestIdentity,
        prior_state_identity: WorkflowStateIdentity,
        disposition: WorkflowAdapterDisposition,
        successor_state_references: tuple[WorkflowTypedReference, ...] = (),
        successor_run_status: WorkflowRunStatus | None = None,
        produced_artifact_references: tuple[
            WorkflowArtifactReference, ...
        ] = (),
        recorded_decision_references: tuple[
            WorkflowDecisionReference, ...
        ] = (),
        reasons: tuple[str, ...] = (),
    ) -> WorkflowAdapterEvidence:
        """Create exact adapter evidence without running an adapter."""
        references = _canonical_references(successor_state_references)
        artifacts = _canonical_artifacts(produced_artifact_references)
        decisions = _canonical_decisions(recorded_decision_references)
        _validate_reasons(reasons)
        identity = _adapter_evidence_identity(
            adapter_identity,
            definition_identity,
            request_identity,
            prior_state_identity,
            disposition,
            references,
            successor_run_status,
            artifacts,
            decisions,
            reasons,
        )
        return cls(
            identity,
            adapter_identity,
            definition_identity,
            request_identity,
            prior_state_identity,
            disposition,
            references,
            successor_run_status,
            artifacts,
            decisions,
            reasons,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "adapter evidence identity",
            self.identity,
            WorkflowAdapterEvidenceIdentity,
        )
        _exact_type(
            "adapter identity", self.adapter_identity, WorkflowAdapterIdentity
        )
        _exact_type(
            "definition identity",
            self.definition_identity,
            WorkflowDefinitionIdentity,
        )
        _exact_type(
            "request identity",
            self.request_identity,
            WorkflowTransitionRequestIdentity,
        )
        _exact_type(
            "prior state identity",
            self.prior_state_identity,
            WorkflowStateIdentity,
        )
        if not isinstance(self.disposition, WorkflowAdapterDisposition):
            raise TypeError("disposition must be WorkflowAdapterDisposition")
        if len(self.successor_state_references) > _MAX_STATE_REFERENCES:
            raise ValueError("too many successor state references")
        if _canonical_references(self.successor_state_references) != (
            self.successor_state_references
        ):
            raise ValueError("successor state references must be canonical")
        if len(self.produced_artifact_references) > _MAX_ARTIFACT_REFERENCES:
            raise ValueError("too many produced artifact references")
        if _canonical_artifacts(self.produced_artifact_references) != (
            self.produced_artifact_references
        ):
            raise ValueError("produced artifact references must be canonical")
        if len(self.recorded_decision_references) > _MAX_DECISION_REFERENCES:
            raise ValueError("too many recorded decision references")
        if _canonical_decisions(self.recorded_decision_references) != (
            self.recorded_decision_references
        ):
            raise ValueError("recorded decision references must be canonical")
        _validate_reasons(self.reasons)
        enabled = self.disposition is WorkflowAdapterDisposition.ENABLED
        if enabled != (self.successor_run_status is not None):
            raise ValueError(
                "enabled evidence alone must provide successor run status"
            )
        if not enabled and (
            self.successor_state_references
            or self.produced_artifact_references
            or self.recorded_decision_references
        ):
            raise ValueError(
                "non-enabled adapter evidence cannot produce state"
            )
        if not enabled and not self.reasons:
            raise ValueError("non-enabled adapter evidence requires reasons")
        if (
            enabled
            and self.successor_run_status is not WorkflowRunStatus.ACTIVE
            and not self.reasons
        ):
            raise ValueError("nonactive successor status requires reasons")
        if self.identity != _adapter_evidence_identity(
            self.adapter_identity,
            self.definition_identity,
            self.request_identity,
            self.prior_state_identity,
            self.disposition,
            self.successor_state_references,
            self.successor_run_status,
            self.produced_artifact_references,
            self.recorded_decision_references,
            self.reasons,
        ):
            raise ValueError("adapter evidence identity is inconsistent")


@dataclass(frozen=True, slots=True)
class WorkflowInfrastructureFailureEvidence:
    """Evidence that adapter execution infrastructure failed."""

    identity: WorkflowInfrastructureFailureIdentity
    request_identity: WorkflowTransitionRequestIdentity
    operation_phase: str
    failure_code: str
    message: str
    evidence_identity: WorkflowExternalReferenceIdentity
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        request_identity: WorkflowTransitionRequestIdentity,
        operation_phase: str,
        failure_code: str,
        message: str,
        evidence_identity: WorkflowExternalReferenceIdentity,
    ) -> WorkflowInfrastructureFailureEvidence:
        """Create a failure without classifying it as rejection."""
        identity = _infrastructure_failure_identity(
            request_identity,
            operation_phase,
            failure_code,
            message,
            evidence_identity,
        )
        return cls(
            identity,
            request_identity,
            operation_phase,
            failure_code,
            message,
            evidence_identity,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "infrastructure failure identity",
            self.identity,
            WorkflowInfrastructureFailureIdentity,
        )
        _exact_type(
            "request identity",
            self.request_identity,
            WorkflowTransitionRequestIdentity,
        )
        _bounded_string("operation phase", self.operation_phase)
        _bounded_string("failure code", self.failure_code)
        _bounded_string(
            "infrastructure failure message",
            self.message,
            maximum=_MAX_MESSAGE_CHARACTERS,
        )
        _exact_type(
            "failure evidence identity",
            self.evidence_identity,
            WorkflowExternalReferenceIdentity,
        )
        if self.identity != _infrastructure_failure_identity(
            self.request_identity,
            self.operation_phase,
            self.failure_code,
            self.message,
            self.evidence_identity,
        ):
            raise ValueError("infrastructure failure identity is inconsistent")


@dataclass(frozen=True, slots=True)
class WorkflowValidationFinding:
    """Stable typed finding produced by cross-record validation."""

    identity: WorkflowValidationFindingIdentity
    code: WorkflowValidationFindingCode
    path: tuple[str, ...]
    related_identities: tuple[str, ...]
    message: str

    @classmethod
    def create(
        cls,
        *,
        code: WorkflowValidationFindingCode,
        path: tuple[str, ...],
        related_identities: tuple[str, ...],
        message: str,
    ) -> WorkflowValidationFinding:
        """Create a deterministic validation finding."""
        identity = _validation_finding_identity(
            code,
            path,
            related_identities,
            message,
        )
        return cls(identity, code, path, related_identities, message)

    def __post_init__(self) -> None:
        _exact_type(
            "validation finding identity",
            self.identity,
            WorkflowValidationFindingIdentity,
        )
        if not isinstance(self.code, WorkflowValidationFindingCode):
            raise TypeError("code must be WorkflowValidationFindingCode")
        _string_tuple("finding path", self.path, allow_empty=False)
        _string_tuple(
            "related identities", self.related_identities, allow_empty=True
        )
        _bounded_string(
            "validation finding message",
            self.message,
            maximum=_MAX_MESSAGE_CHARACTERS,
        )
        if self.identity != _validation_finding_identity(
            self.code,
            self.path,
            self.related_identities,
            self.message,
        ):
            raise ValueError("validation finding identity is inconsistent")

    def identity_parts(self) -> tuple[object, ...]:
        """Return complete stable finding evidence."""
        return (
            self.identity,
            self.code,
            self.path,
            self.related_identities,
            self.message,
        )


@dataclass(frozen=True, slots=True)
class WorkflowValidationResult:
    """Deterministic ordered collection of cross-record validation findings."""

    MAX_FINDINGS: ClassVar[int] = _MAX_FINDINGS

    identity: WorkflowValidationIdentity
    findings: tuple[WorkflowValidationFinding, ...]

    @classmethod
    def create(
        cls, findings: tuple[WorkflowValidationFinding, ...]
    ) -> WorkflowValidationResult:
        """Create a deterministic validation result preserving finding order."""
        if type(findings) is not tuple or any(
            type(item) is not WorkflowValidationFinding for item in findings
        ):
            raise TypeError(
                "findings must be a tuple of WorkflowValidationFinding"
            )
        if len(findings) > _MAX_FINDINGS:
            raise ValueError("too many workflow validation findings")
        identity = _validation_result_identity(findings)
        return cls(identity, findings)

    def __post_init__(self) -> None:
        _exact_type(
            "validation identity", self.identity, WorkflowValidationIdentity
        )
        if type(self.findings) is not tuple or any(
            type(item) is not WorkflowValidationFinding
            for item in self.findings
        ):
            raise TypeError(
                "findings must be a tuple of WorkflowValidationFinding"
            )
        if len(self.findings) > _MAX_FINDINGS:
            raise ValueError("too many workflow validation findings")
        if self.identity != _validation_result_identity(self.findings):
            raise ValueError("validation result identity is inconsistent")

    @property
    def is_valid(self) -> bool:
        """Return whether validation produced no findings."""
        return not self.findings


@dataclass(frozen=True, slots=True)
class WorkflowTransitionOutcome:
    """Immutable applied or non-applied result of core transition processing."""

    MAX_REASONS: ClassVar[int] = _MAX_REASONS

    identity: WorkflowTransitionOutcomeIdentity
    kind: WorkflowTransitionOutcomeKind
    run_identity: WorkflowRunIdentity
    request_identity: WorkflowTransitionRequestIdentity
    prior_state_identity: WorkflowStateIdentity
    prior_revision: int
    validation: WorkflowValidationResult
    adapter_evidence_identity: WorkflowAdapterEvidenceIdentity | None = None
    infrastructure_failure_identity: (
        WorkflowInfrastructureFailureIdentity | None
    ) = None
    successor_state: WorkflowStateSnapshot | None = None
    successor_run: WorkflowRun | None = None
    reasons: tuple[str, ...] = ()
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        kind: WorkflowTransitionOutcomeKind,
        run_identity: WorkflowRunIdentity,
        request_identity: WorkflowTransitionRequestIdentity,
        prior_state_identity: WorkflowStateIdentity,
        prior_revision: int,
        validation: WorkflowValidationResult,
        adapter_evidence_identity: WorkflowAdapterEvidenceIdentity
        | None = None,
        infrastructure_failure_identity: (
            WorkflowInfrastructureFailureIdentity | None
        ) = None,
        successor_state: WorkflowStateSnapshot | None = None,
        successor_run: WorkflowRun | None = None,
        reasons: tuple[str, ...] = (),
    ) -> WorkflowTransitionOutcome:
        """Create one closed transition-outcome variant."""
        _validate_reasons(reasons)
        identity = _transition_outcome_identity(
            kind,
            run_identity,
            request_identity,
            prior_state_identity,
            prior_revision,
            validation,
            adapter_evidence_identity,
            infrastructure_failure_identity,
            successor_state,
            successor_run,
            reasons,
        )
        return cls(
            identity,
            kind,
            run_identity,
            request_identity,
            prior_state_identity,
            prior_revision,
            validation,
            adapter_evidence_identity,
            infrastructure_failure_identity,
            successor_state,
            successor_run,
            reasons,
        )

    def __post_init__(self) -> None:
        _contract_version(self.contract_version)
        _exact_type(
            "outcome identity",
            self.identity,
            WorkflowTransitionOutcomeIdentity,
        )
        if not isinstance(self.kind, WorkflowTransitionOutcomeKind):
            raise TypeError("kind must be WorkflowTransitionOutcomeKind")
        _exact_type("run identity", self.run_identity, WorkflowRunIdentity)
        _exact_type(
            "request identity",
            self.request_identity,
            WorkflowTransitionRequestIdentity,
        )
        _exact_type(
            "prior state identity",
            self.prior_state_identity,
            WorkflowStateIdentity,
        )
        _nonnegative_integer("prior revision", self.prior_revision)
        _exact_type("validation", self.validation, WorkflowValidationResult)
        if self.adapter_evidence_identity is not None:
            _exact_type(
                "adapter evidence identity",
                self.adapter_evidence_identity,
                WorkflowAdapterEvidenceIdentity,
            )
        if self.infrastructure_failure_identity is not None:
            _exact_type(
                "infrastructure failure identity",
                self.infrastructure_failure_identity,
                WorkflowInfrastructureFailureIdentity,
            )
        if self.successor_state is not None:
            _exact_type(
                "successor state",
                self.successor_state,
                WorkflowStateSnapshot,
            )
        if self.successor_run is not None:
            _exact_type("successor run", self.successor_run, WorkflowRun)
        _validate_reasons(self.reasons)
        applied = self.kind is WorkflowTransitionOutcomeKind.APPLIED
        if applied != (
            self.successor_state is not None and self.successor_run is not None
        ):
            raise ValueError("only applied outcomes have a successor")
        if applied and self.adapter_evidence_identity is None:
            raise ValueError("applied outcome requires adapter evidence")
        if applied and not self.validation.is_valid:
            raise ValueError("applied outcome requires valid input")
        adapter_nonapplication = self.kind in {
            WorkflowTransitionOutcomeKind.NOT_ENABLED,
            WorkflowTransitionOutcomeKind.BLOCKED,
        }
        if adapter_nonapplication and self.adapter_evidence_identity is None:
            raise ValueError("adapter outcome requires adapter evidence")
        if adapter_nonapplication and not self.validation.is_valid:
            raise ValueError("adapter outcome requires valid input")
        validation_rejection = self.kind in {
            WorkflowTransitionOutcomeKind.REJECTED_INVALID,
            WorkflowTransitionOutcomeKind.CONFLICT,
        }
        if validation_rejection and self.validation.is_valid:
            raise ValueError("validation rejection requires findings")
        infrastructure = (
            self.kind is WorkflowTransitionOutcomeKind.INFRASTRUCTURE_FAILURE
        )
        if infrastructure and self.infrastructure_failure_identity is None:
            raise ValueError(
                "infrastructure outcome requires its failure evidence"
            )
        if (
            not infrastructure
            and self.infrastructure_failure_identity is not None
            and not validation_rejection
        ):
            raise ValueError(
                "only infrastructure or validation-rejection outcomes may "
                "retain failure evidence"
            )
        if (
            self.infrastructure_failure_identity is not None
            and self.adapter_evidence_identity is not None
        ):
            raise ValueError(
                "outcome cannot claim adapter and failure evidence together"
            )
        if infrastructure and not self.validation.is_valid:
            raise ValueError("infrastructure outcome requires valid input")
        if self.successor_state is not None and self.successor_run is not None:
            if (
                self.successor_run.current_state_identity
                != self.successor_state.identity
                or self.successor_run.identity != self.run_identity
                or self.successor_run.identity
                != self.successor_state.run_identity
                or self.successor_run.definition_identity
                != self.successor_state.definition_identity
                or self.successor_run.revision != self.prior_revision + 1
                or self.successor_run.revision != self.successor_state.revision
                or self.successor_run.status != self.successor_state.run_status
                or self.successor_state.predecessor_state_identity
                != self.prior_state_identity
            ):
                raise ValueError("successor run and state must agree")
        if self.identity != _transition_outcome_identity(
            self.kind,
            self.run_identity,
            self.request_identity,
            self.prior_state_identity,
            self.prior_revision,
            self.validation,
            self.adapter_evidence_identity,
            self.infrastructure_failure_identity,
            self.successor_state,
            self.successor_run,
            self.reasons,
        ):
            raise ValueError("transition outcome identity is inconsistent")


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


def _artifact_reference_identity(
    artifact_identity: WorkflowExternalReferenceIdentity,
    artifact_kind: str,
    digest_sha256: str,
    role: str,
    disposition: WorkflowArtifactDisposition,
    provenance_identity: WorkflowExternalReferenceIdentity,
) -> WorkflowArtifactReferenceIdentity:
    return WorkflowArtifactReferenceIdentity(
        stable_identity(
            "workflow-artifact-reference",
            artifact_identity,
            artifact_kind,
            digest_sha256,
            role,
            disposition,
            provenance_identity,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _authority_reference_identity(
    authority_kind: str,
    subject_identity: WorkflowSubjectIdentity,
    operations: tuple[WorkflowOperationIdentity, ...],
    evidence_identity: WorkflowExternalReferenceIdentity,
    authority_version: str,
) -> WorkflowAuthorityReferenceIdentity:
    return WorkflowAuthorityReferenceIdentity(
        stable_identity(
            "workflow-authority-reference",
            authority_kind,
            subject_identity,
            operations,
            evidence_identity,
            authority_version,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _decision_reference_identity(
    decision_kind: str,
    scope: str,
    subject_identity: WorkflowSubjectIdentity,
    authority_identity: WorkflowExternalReferenceIdentity,
    outcome: str,
    evidence_identity: WorkflowExternalReferenceIdentity,
    decision_version: str,
) -> WorkflowDecisionReferenceIdentity:
    return WorkflowDecisionReferenceIdentity(
        stable_identity(
            "workflow-decision-reference",
            decision_kind,
            scope,
            subject_identity,
            authority_identity,
            outcome,
            evidence_identity,
            decision_version,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _definition_reference_identity(
    contract_id: str,
    definition_version: str,
    digest_sha256: str,
    operations: tuple[WorkflowOperationIdentity, ...],
) -> WorkflowDefinitionIdentity:
    return WorkflowDefinitionIdentity(
        stable_identity(
            "workflow-definition-reference",
            contract_id,
            definition_version,
            digest_sha256,
            operations,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _state_snapshot_identity(
    run_identity: WorkflowRunIdentity,
    definition_identity: WorkflowDefinitionIdentity,
    revision: int,
    run_status: WorkflowRunStatus,
    references: tuple[WorkflowTypedReference, ...],
    predecessor_state_identity: WorkflowStateIdentity | None,
) -> WorkflowStateIdentity:
    return WorkflowStateIdentity(
        stable_identity(
            "workflow-state-snapshot",
            run_identity,
            definition_identity,
            revision,
            run_status,
            tuple(item.identity_parts() for item in references),
            predecessor_state_identity,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _transition_request_identity(
    run_identity: WorkflowRunIdentity,
    prior_state_identity: WorkflowStateIdentity,
    revision: int,
    operation_identity: WorkflowOperationIdentity,
    inputs: tuple[WorkflowTypedReference, ...],
    artifacts: tuple[WorkflowArtifactReference, ...],
    decisions: tuple[WorkflowDecisionReference, ...],
    actor_identity: WorkflowActorIdentity,
    authority_reference: WorkflowAuthorityReference,
    idempotency_identity: WorkflowIdempotencyIdentity,
    bounds: WorkflowRequestBounds,
) -> WorkflowTransitionRequestIdentity:
    return WorkflowTransitionRequestIdentity(
        stable_identity(
            "workflow-transition-request",
            run_identity,
            prior_state_identity,
            revision,
            operation_identity,
            tuple(item.identity_parts() for item in inputs),
            tuple(item.identity_parts() for item in artifacts),
            tuple(item.identity_parts() for item in decisions),
            actor_identity,
            authority_reference.identity,
            idempotency_identity,
            bounds.identity_parts(),
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _adapter_evidence_identity(
    adapter_identity: WorkflowAdapterIdentity,
    definition_identity: WorkflowDefinitionIdentity,
    request_identity: WorkflowTransitionRequestIdentity,
    prior_state_identity: WorkflowStateIdentity,
    disposition: WorkflowAdapterDisposition,
    references: tuple[WorkflowTypedReference, ...],
    successor_status: WorkflowRunStatus | None,
    artifacts: tuple[WorkflowArtifactReference, ...],
    decisions: tuple[WorkflowDecisionReference, ...],
    reasons: tuple[str, ...],
) -> WorkflowAdapterEvidenceIdentity:
    return WorkflowAdapterEvidenceIdentity(
        stable_identity(
            "workflow-adapter-evidence",
            adapter_identity,
            definition_identity,
            request_identity,
            prior_state_identity,
            disposition,
            tuple(item.identity_parts() for item in references),
            successor_status,
            tuple(item.identity_parts() for item in artifacts),
            tuple(item.identity_parts() for item in decisions),
            reasons,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _infrastructure_failure_identity(
    request_identity: WorkflowTransitionRequestIdentity,
    operation_phase: str,
    failure_code: str,
    message: str,
    evidence_identity: WorkflowExternalReferenceIdentity,
) -> WorkflowInfrastructureFailureIdentity:
    return WorkflowInfrastructureFailureIdentity(
        stable_identity(
            "workflow-infrastructure-failure",
            request_identity,
            operation_phase,
            failure_code,
            message,
            evidence_identity,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _validation_finding_identity(
    code: WorkflowValidationFindingCode,
    path: tuple[str, ...],
    related_identities: tuple[str, ...],
    message: str,
) -> WorkflowValidationFindingIdentity:
    return WorkflowValidationFindingIdentity(
        stable_identity(
            "workflow-validation-finding",
            code,
            path,
            related_identities,
            message,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _validation_result_identity(
    findings: tuple[WorkflowValidationFinding, ...],
) -> WorkflowValidationIdentity:
    return WorkflowValidationIdentity(
        stable_identity(
            "workflow-validation-result",
            tuple(item.identity_parts() for item in findings),
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _transition_outcome_identity(
    kind: WorkflowTransitionOutcomeKind,
    run_identity: WorkflowRunIdentity,
    request_identity: WorkflowTransitionRequestIdentity,
    prior_state_identity: WorkflowStateIdentity,
    prior_revision: int,
    validation: WorkflowValidationResult,
    adapter_evidence_identity: WorkflowAdapterEvidenceIdentity | None,
    failure_identity: WorkflowInfrastructureFailureIdentity | None,
    successor_state: WorkflowStateSnapshot | None,
    successor_run: WorkflowRun | None,
    reasons: tuple[str, ...],
) -> WorkflowTransitionOutcomeIdentity:
    return WorkflowTransitionOutcomeIdentity(
        stable_identity(
            "workflow-transition-outcome",
            kind,
            run_identity,
            request_identity,
            prior_state_identity,
            prior_revision,
            validation.identity,
            adapter_evidence_identity,
            failure_identity,
            None if successor_state is None else successor_state.identity,
            None if successor_run is None else successor_run.snapshot_parts(),
            reasons,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


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


def _run_identity(
    run_key: str,
    definition_identity: WorkflowDefinitionIdentity,
    subject_identity: WorkflowSubjectIdentity,
    parent_run_identity: WorkflowRunIdentity | None,
    predecessor_run_identity: WorkflowRunIdentity | None,
) -> WorkflowRunIdentity:
    _bounded_string("run key", run_key)
    return WorkflowRunIdentity(
        stable_identity(
            "workflow-run",
            run_key,
            definition_identity,
            subject_identity,
            parent_run_identity,
            predecessor_run_identity,
            WORKFLOW_CORE_CONTRACT_VERSION,
        )
    )


def _canonical_operation_identities(
    name: str,
    values: tuple[WorkflowOperationIdentity, ...],
    maximum: int,
) -> tuple[WorkflowOperationIdentity, ...]:
    if type(values) is not tuple or any(
        type(item) is not WorkflowOperationIdentity for item in values
    ):
        raise TypeError(f"{name} must be a tuple of WorkflowOperationIdentity")
    if not values or len(values) > maximum:
        raise ValueError(f"{name} must be nonempty and bounded")
    identities = tuple(item.value for item in values)
    if len(set(identities)) != len(identities):
        raise ValueError(f"{name} must be unique")
    return tuple(sorted(values, key=lambda item: item.value))


def _canonical_references(
    values: tuple[WorkflowTypedReference, ...],
) -> tuple[WorkflowTypedReference, ...]:
    if type(values) is not tuple or any(
        type(item) is not WorkflowTypedReference for item in values
    ):
        raise TypeError("state references must be WorkflowTypedReference tuple")
    if len(values) > _MAX_STATE_REFERENCES:
        raise ValueError("too many state references")
    keys = tuple(
        (item.reference_kind, item.reference_identity.value) for item in values
    )
    if len(set(keys)) != len(keys):
        raise ValueError("state references must be unique by kind and identity")
    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.reference_kind,
                item.reference_identity.value,
                "" if item.digest_sha256 is None else item.digest_sha256,
            ),
        )
    )


def _canonical_artifacts(
    values: tuple[WorkflowArtifactReference, ...],
) -> tuple[WorkflowArtifactReference, ...]:
    if type(values) is not tuple or any(
        type(item) is not WorkflowArtifactReference for item in values
    ):
        raise TypeError(
            "artifact references must be WorkflowArtifactReference tuple"
        )
    if len(values) > _MAX_ARTIFACT_REFERENCES:
        raise ValueError("too many artifact references")
    identities = tuple(item.identity for item in values)
    if len(set(identities)) != len(identities):
        raise ValueError("artifact references must be unique")
    return tuple(sorted(values, key=lambda item: item.identity.value))


def _canonical_decisions(
    values: tuple[WorkflowDecisionReference, ...],
) -> tuple[WorkflowDecisionReference, ...]:
    if type(values) is not tuple or any(
        type(item) is not WorkflowDecisionReference for item in values
    ):
        raise TypeError(
            "decision references must be WorkflowDecisionReference tuple"
        )
    if len(values) > _MAX_DECISION_REFERENCES:
        raise ValueError("too many decision references")
    identities = tuple(item.identity for item in values)
    if len(set(identities)) != len(identities):
        raise ValueError("decision references must be unique")
    return tuple(sorted(values, key=lambda item: item.identity.value))


def _validate_request_collections(
    inputs: tuple[WorkflowTypedReference, ...],
    artifacts: tuple[WorkflowArtifactReference, ...],
    decisions: tuple[WorkflowDecisionReference, ...],
    bounds: WorkflowRequestBounds,
) -> None:
    if type(inputs) is not tuple or any(
        type(item) is not WorkflowTypedReference for item in inputs
    ):
        raise TypeError("input references must be WorkflowTypedReference tuple")
    input_keys = tuple(
        (item.reference_kind, item.reference_identity.value) for item in inputs
    )
    if len(set(input_keys)) != len(input_keys):
        raise ValueError("input references must be unique")
    if len(inputs) > bounds.max_input_references:
        raise ValueError("input references exceed request bounds")
    _canonical_artifacts(artifacts)
    if len(artifacts) > bounds.max_artifact_references:
        raise ValueError("artifact references exceed request bounds")
    if _canonical_decisions(decisions) != decisions:
        raise ValueError("decision references must be canonical")
    if len(decisions) > bounds.max_decision_references:
        raise ValueError("decision references exceed request bounds")


def _validate_reasons(reasons: tuple[str, ...]) -> None:
    _string_tuple("reasons", reasons, allow_empty=True)
    if len(reasons) > _MAX_REASONS:
        raise ValueError("too many reasons")


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


def _string_tuple(
    name: str, value: tuple[str, ...], *, allow_empty: bool
) -> None:
    if type(value) is not tuple or any(type(item) is not str for item in value):
        raise TypeError(f"{name} must be a tuple of strings")
    if not allow_empty and not value:
        raise ValueError(f"{name} must not be empty")
    if len(value) > _MAX_STATE_REFERENCES:
        raise ValueError(f"{name} contains too many items")
    if any(not item or len(item) > _MAX_MESSAGE_CHARACTERS for item in value):
        raise ValueError(f"{name} must contain bounded nonempty strings")


def _nonnegative_integer(name: str, value: int) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


def _positive_integer(name: str, value: int) -> None:
    _nonnegative_integer(name, value)
    if value == 0:
        raise ValueError(f"{name} must be positive")


def _sha256(name: str, value: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if len(value) != 64 or any(
        character not in _SHA256_CHARACTERS for character in value
    ):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
