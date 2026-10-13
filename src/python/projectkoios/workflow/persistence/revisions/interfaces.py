"""Opaque single-stream revision persistence contracts.

The shared store knows only immutable stream revisions and exact payload
bytes. It owns compare-and-append and idempotency closure; workflow meaning
remains in the runtime repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

_MAX_IDENTIFIER_CHARACTERS = 4_096
_MAX_DIAGNOSTICS = 32
_MAX_DIAGNOSTIC_CHARACTERS = 1_024


def _identifier(value: object, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a built-in str")
    if not value or len(value) > _MAX_IDENTIFIER_CHARACTERS:
        raise ValueError(f"{field} must be nonempty and bounded")
    return value


def _optional_identifier(value: object, field: str) -> str | None:
    if value is None:
        return None
    return _identifier(value, field)


def _diagnostics(values: object) -> tuple[str, ...]:
    if type(values) is not tuple:
        raise TypeError("diagnostics must be a tuple")
    if len(values) > _MAX_DIAGNOSTICS:
        raise ValueError("diagnostics exceed their bound")
    for value in values:
        if type(value) is not str:
            raise TypeError("diagnostics must contain built-in strings")
        if not value or len(value) > _MAX_DIAGNOSTIC_CHARACTERS:
            raise ValueError("diagnostics must be nonempty and bounded")
    return values


class RevisionSelector(StrEnum):
    """Select the current head or one exact historical revision."""

    LATEST = "latest"
    EXPLICIT = "explicit"


class RevisionReadStatus(StrEnum):
    """Closed result of one revision observation."""

    FOUND = "found"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


class RevisionCommitStatus(StrEnum):
    """Closed result of one compare-and-append operation."""

    COMMITTED = "committed"
    IDEMPOTENT = "idempotent"
    CONFLICT = "conflict"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Revision:
    """One complete opaque revision in one logical stream."""

    stream_identity: str
    revision_identity: str
    predecessor_revision_identity: str | None
    schema_identity: str
    content_identity: str
    payload: bytes

    def __post_init__(self) -> None:
        _identifier(self.stream_identity, "stream_identity")
        _identifier(self.revision_identity, "revision_identity")
        _optional_identifier(
            self.predecessor_revision_identity,
            "predecessor_revision_identity",
        )
        _identifier(self.schema_identity, "schema_identity")
        _identifier(self.content_identity, "content_identity")
        if type(self.payload) is not bytes:
            raise TypeError("payload must be built-in bytes")
        if self.predecessor_revision_identity == self.revision_identity:
            raise ValueError("a revision cannot name itself as predecessor")


@dataclass(frozen=True, slots=True)
class RevisionReadRequest:
    """Identify one exact stream observation without ambient discovery."""

    request_identity: str
    stream_identity: str
    selector: RevisionSelector
    revision_identity: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.request_identity, "request_identity")
        _identifier(self.stream_identity, "stream_identity")
        if type(self.selector) is not RevisionSelector:
            raise TypeError("selector must be RevisionSelector")
        _optional_identifier(self.revision_identity, "revision_identity")
        if self.selector is RevisionSelector.LATEST:
            if self.revision_identity is not None:
                raise ValueError("latest selection prohibits revision_identity")
        elif self.revision_identity is None:
            raise ValueError("explicit selection requires revision_identity")


@dataclass(frozen=True, slots=True)
class RevisionReadResult:
    """Closed revision-read result; only ``found`` contains a revision."""

    status: RevisionReadStatus
    request_identity: str
    stream_identity: str
    diagnostics: tuple[str, ...]
    revision: Revision | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not RevisionReadStatus:
            raise TypeError("status must be RevisionReadStatus")
        _identifier(self.request_identity, "request_identity")
        _identifier(self.stream_identity, "stream_identity")
        _diagnostics(self.diagnostics)
        if self.revision is not None and type(self.revision) is not Revision:
            raise TypeError("revision must be Revision or None")
        if self.status is RevisionReadStatus.FOUND:
            if self.revision is None:
                raise ValueError("found requires a revision")
            if self.revision.stream_identity != self.stream_identity:
                raise ValueError("found revision belongs to another stream")
        elif self.revision is not None:
            raise ValueError("non-found results prohibit a revision")


@dataclass(frozen=True, slots=True)
class RevisionCommit:
    """Bind one candidate to expected-head and idempotency identities."""

    expected_revision_identity: str | None
    candidate: Revision
    idempotency_identity: str

    def __post_init__(self) -> None:
        _optional_identifier(
            self.expected_revision_identity,
            "expected_revision_identity",
        )
        if type(self.candidate) is not Revision:
            raise TypeError("candidate must be Revision")
        _identifier(self.idempotency_identity, "idempotency_identity")
        if (
            self.candidate.predecessor_revision_identity
            != self.expected_revision_identity
        ):
            raise ValueError(
                "candidate predecessor must equal expected revision"
            )


@dataclass(frozen=True, slots=True)
class RevisionCommitResult:
    """Closed compare-and-append result."""

    status: RevisionCommitStatus
    stream_identity: str
    idempotency_identity: str
    diagnostics: tuple[str, ...]
    revision: Revision | None = None
    observed_revision_identity: str | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not RevisionCommitStatus:
            raise TypeError("status must be RevisionCommitStatus")
        _identifier(self.stream_identity, "stream_identity")
        _identifier(self.idempotency_identity, "idempotency_identity")
        _diagnostics(self.diagnostics)
        if self.revision is not None and type(self.revision) is not Revision:
            raise TypeError("revision must be Revision or None")
        _optional_identifier(
            self.observed_revision_identity,
            "observed_revision_identity",
        )
        if self.status in {
            RevisionCommitStatus.COMMITTED,
            RevisionCommitStatus.IDEMPOTENT,
        }:
            if self.revision is None:
                raise ValueError("successful commit result requires a revision")
            if self.observed_revision_identity is not None:
                raise ValueError(
                    "successful commit result prohibits conflict state"
                )
        elif self.status is RevisionCommitStatus.CONFLICT:
            if self.revision is not None:
                raise ValueError("conflict prohibits a revision")
        elif (
            self.revision is not None
            or self.observed_revision_identity is not None
        ):
            raise ValueError(
                "indeterminate and error prohibit revision-presence claims"
            )


@runtime_checkable
class AtomicRevisionStore(Protocol):
    """Structural boundary for opaque atomic revision storage."""

    def read(self, request: RevisionReadRequest) -> RevisionReadResult:
        """Observe one latest or explicit revision."""
        ...

    def commit(self, commit: RevisionCommit) -> RevisionCommitResult:
        """Compare and append one complete candidate revision."""
        ...
