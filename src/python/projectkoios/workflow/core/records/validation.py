"""Validation owned by the immutable Workflow core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..identities.definition import (
    WorkflowValidationFindingIdentity,
    WorkflowValidationIdentity,
    stable_identity,
)
from .contract import (
    _MAX_FINDINGS,
    _MAX_MESSAGE_CHARACTERS,
    _MAX_STATE_REFERENCES,
    _MAX_STRING_CHARACTERS,
    WORKFLOW_CORE_CONTRACT_VERSION,
)
from .kinds import WorkflowValidationFindingCode


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
