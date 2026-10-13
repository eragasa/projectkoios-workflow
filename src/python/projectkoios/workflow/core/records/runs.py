"""Runs owned by the immutable Workflow core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..identities.definition import (
    WorkflowDefinitionIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    WorkflowSubjectIdentity,
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
from .kinds import WorkflowRunStatus
from .references import (
    WorkflowArtifactReference,
    WorkflowDecisionReference,
    WorkflowDefinitionReference,
    WorkflowTypedReference,
)
from .states import WorkflowStateSnapshot


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


def _nonnegative_integer(name: str, value: int) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
