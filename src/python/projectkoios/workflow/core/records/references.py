"""References owned by the immutable Workflow core."""

from __future__ import annotations

from dataclasses import dataclass

from ..identities.definition import (
    WorkflowArtifactReferenceIdentity,
    WorkflowAuthorityReferenceIdentity,
    WorkflowDecisionReferenceIdentity,
    WorkflowDefinitionIdentity,
    WorkflowExternalReferenceIdentity,
    WorkflowOperationIdentity,
    WorkflowSubjectIdentity,
    stable_identity,
)
from .contract import (
    _MAX_OPERATIONS,
    _MAX_STRING_CHARACTERS,
    _SHA256_CHARACTERS,
    WORKFLOW_CORE_CONTRACT_VERSION,
)
from .kinds import WorkflowArtifactDisposition


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
    """Reference to authority evidence verified by its owning policy.

    The core validates nominal subject and operation binding only. Constructing
    this record does not authenticate, authorize, refresh, or revoke evidence.
    A runtime must resolve and verify the external evidence before dispatch.
    """

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
        """Create a scoped reference without verifying or granting authority."""
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


def _sha256(name: str, value: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if len(value) != 64 or any(
        character not in _SHA256_CHARACTERS for character in value
    ):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
