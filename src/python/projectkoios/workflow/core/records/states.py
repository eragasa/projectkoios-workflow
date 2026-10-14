"""States owned by the immutable Workflow core."""

from __future__ import annotations

from dataclasses import dataclass

from ..identities.definition import (
    WorkflowDefinitionIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    stable_identity,
)
from .contract import (
    _MAX_STATE_REFERENCES,
    WORKFLOW_CORE_CONTRACT_VERSION,
)
from .kinds import WorkflowRunStatus
from .references import WorkflowTypedReference


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
