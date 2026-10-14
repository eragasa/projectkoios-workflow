"""Nominal identities and deterministic identity construction for workflow core.

The public identity classes prevent accidental interchange among workflow
subjects. ``stable_identity`` is an owner-internal canonical identity helper;
it is not a public wire-format commitment and performs no I/O.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Protocol

_MAX_IDENTITY_CHARACTERS = 4_096


class WorkflowIdentity(Protocol):
    """Structural protocol for nominal identity values used internally."""

    value: str


def _validate_identity(value: str) -> None:
    if type(value) is not str:
        raise TypeError("identity value must be a string")
    if not value or len(value) > _MAX_IDENTITY_CHARACTERS:
        raise ValueError("identity value must be nonempty and bounded")


@dataclass(frozen=True, slots=True)
class WorkflowDefinitionIdentity:
    """Nominal identity of one immutable workflow definition reference."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowRunIdentity:
    """Nominal identity of one workflow attempt across immutable revisions."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowStateIdentity:
    """Nominal content identity of one immutable workflow state snapshot."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowTransitionRequestIdentity:
    """Nominal content identity of one transition request."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowTransitionOutcomeIdentity:
    """Nominal content identity of one transition outcome."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowArtifactReferenceIdentity:
    """Nominal identity of one bounded external-artifact reference."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowDecisionReferenceIdentity:
    """Nominal identity of one separately owned decision reference."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowAuthorityReferenceIdentity:
    """Nominal identity of one authority-evidence reference."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowAdapterEvidenceIdentity:
    """Nominal identity of one engine-adapter evidence record."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowInfrastructureFailureIdentity:
    """Nominal identity of one externally observed infrastructure failure."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowValidationIdentity:
    """Nominal identity of one deterministic validation result."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowValidationFindingIdentity:
    """Nominal identity of one deterministic validation finding."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowAuditEventIdentity:
    """Nominal identity of one bounded immutable audit event."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowReplayIdentity:
    """Nominal identity of one deterministic replay comparison."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowOperationIdentity:
    """Nominal identity of one definition-owned transition intent."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowSubjectIdentity:
    """Opaque nominal identity of the application-owned workflow subject."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowActorIdentity:
    """Opaque nominal identity of the actor initiating a request."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowAdapterIdentity:
    """Nominal identity of one exact workflow-engine adapter implementation."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowIdempotencyIdentity:
    """Caller-supplied nominal identity for one idempotent request intent."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


@dataclass(frozen=True, slots=True)
class WorkflowExternalReferenceIdentity:
    """Opaque nominal identity owned by an external artifact or state domain."""

    value: str

    def __post_init__(self) -> None:
        _validate_identity(self.value)


def stable_identity(domain: str, *parts: object) -> str:
    """Return a deterministic SHA-256 identity for bounded semantic parts.

    Parameters
    ----------
    domain
        Nonempty owner-local identity domain.
    *parts
        JSON-compatible immutable semantic parts. Nominal identities and enums
        are normalized explicitly.

    Returns
    -------
    str
        Lowercase hexadecimal SHA-256 digest.

    Raises
    ------
    TypeError
        A part has no supported deterministic representation.
    ValueError
        ``domain`` is empty.

    Notes
    -----
    This helper performs no I/O and does not define a public serialization
    format. It exists only to close identities inside this implementation.
    """
    if type(domain) is not str:
        raise TypeError("identity domain must be a string")
    if not domain:
        raise ValueError("identity domain must not be empty")
    payload = {"domain": domain, "parts": [_normalize(part) for part in parts]}
    return sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _normalize(value: object) -> object:
    if value is None or type(value) in (str, bool, int):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if hasattr(value, "value") and type(value.value) is str:
        return {"identity": type(value).__name__, "value": value.value}
    raise TypeError(
        f"unsupported workflow identity part: {type(value).__name__}"
    )
