"""Workflow transition evidence records."""

from __future__ import annotations

from dataclasses import dataclass

from ..identities.definition import (
    WorkflowAdapterEvidenceIdentity,
    WorkflowAdapterIdentity,
    WorkflowDefinitionIdentity,
    WorkflowExternalReferenceIdentity,
    WorkflowInfrastructureFailureIdentity,
    WorkflowStateIdentity,
    WorkflowTransitionRequestIdentity,
    stable_identity,
)
from .contract import (
    _MAX_ARTIFACT_REFERENCES,
    _MAX_DECISION_REFERENCES,
    _MAX_MESSAGE_CHARACTERS,
    _MAX_REASONS,
    _MAX_STATE_REFERENCES,
    _MAX_STRING_CHARACTERS,
    WORKFLOW_CORE_CONTRACT_VERSION,
)
from .kinds import (
    WorkflowAdapterDisposition,
    WorkflowRunStatus,
)
from .references import (
    WorkflowArtifactReference,
    WorkflowDecisionReference,
    WorkflowTypedReference,
)


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
