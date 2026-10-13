"""Workflow transition outcomes records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..identities.definition import (
    WorkflowAdapterEvidenceIdentity,
    WorkflowInfrastructureFailureIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    WorkflowTransitionOutcomeIdentity,
    WorkflowTransitionRequestIdentity,
    stable_identity,
)
from .contract import (
    _MAX_MESSAGE_CHARACTERS,
    _MAX_REASONS,
    _MAX_STATE_REFERENCES,
    WORKFLOW_CORE_CONTRACT_VERSION,
)
from .kinds import (
    WorkflowTransitionOutcomeKind,
)
from .runs import WorkflowRun
from .states import WorkflowStateSnapshot
from .validation import WorkflowValidationResult


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
