"""Workflow transition requests records."""

from __future__ import annotations

from dataclasses import dataclass

from ..identities.definition import (
    WorkflowActorIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowOperationIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    WorkflowTransitionRequestIdentity,
    stable_identity,
)
from .contract import (
    _MAX_ARTIFACT_REFERENCES,
    _MAX_DECISION_REFERENCES,
    _MAX_INPUT_REFERENCES,
    _MAX_STATE_REFERENCES,
    WORKFLOW_CORE_CONTRACT_VERSION,
)
from .references import (
    WorkflowArtifactReference,
    WorkflowAuthorityReference,
    WorkflowDecisionReference,
    WorkflowTypedReference,
)


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
    """Immutable request for one revision-bound workflow state change.

    Its authority reference is evidence supplied by an owning policy, not a
    grant created or authenticated by this request.
    """

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


def _contract_version(value: str) -> None:
    if value != WORKFLOW_CORE_CONTRACT_VERSION:
        raise ValueError("unsupported workflow-core contract version")


def _exact_type(name: str, value: object, expected: type) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be {expected.__name__}")


def _nonnegative_integer(name: str, value: int) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


def _positive_integer(name: str, value: int) -> None:
    _nonnegative_integer(name, value)
    if value == 0:
        raise ValueError(f"{name} must be positive")
