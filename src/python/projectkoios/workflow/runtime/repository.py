"""Runtime-event repository composed with opaque atomic revision storage."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum

from projectkoios.workflow.persistence import (
    AtomicRevisionStore,
    Revision,
    RevisionCommit,
    RevisionCommitStatus,
    RevisionReadRequest,
    RevisionReadStatus,
    RevisionSelector,
)

from .records import WorkflowRuntimeEvent, WorkflowRuntimeEventIdentity
from .serialization import WorkflowRuntimeEventSerializer

_MAX_EVENTS_PER_HISTORY = 10_000


class WorkflowHistoryLoadStatus(StrEnum):
    """Closed result of reconstructing one event history."""

    LOADED = "loaded"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


class WorkflowEventAppendStatus(StrEnum):
    """Closed result of appending one runtime event."""

    APPENDED = "appended"
    IDEMPOTENT = "idempotent"
    CONFLICT = "conflict"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class WorkflowRuntimeHistory:
    """One complete verified per-run event chain."""

    stream_identity: str
    events: tuple[WorkflowRuntimeEvent, ...]

    def __post_init__(self) -> None:
        if type(self.stream_identity) is not str or not self.stream_identity:
            raise ValueError("stream_identity must be a nonempty built-in str")
        if type(self.events) is not tuple or not self.events:
            raise ValueError("events must be a nonempty tuple")
        if len(self.events) > _MAX_EVENTS_PER_HISTORY:
            raise ValueError("events exceed their history bound")
        run_identity = self.events[0].run_identity
        for ordinal, event in enumerate(self.events):
            if type(event) is not WorkflowRuntimeEvent:
                raise TypeError("events must contain WorkflowRuntimeEvent")
            predecessor = (
                None if ordinal == 0 else self.events[ordinal - 1].identity
            )
            if (
                event.ordinal != ordinal
                or event.run_identity != run_identity
                or event.predecessor_event_identity != predecessor
            ):
                raise ValueError("runtime event chain is inconsistent")
        if self.stream_identity != run_identity.value:
            raise ValueError("history stream must equal its run identity")

    @property
    def head(self) -> WorkflowRuntimeEvent:
        """Return the latest verified event."""
        return self.events[-1]


@dataclass(frozen=True, slots=True)
class WorkflowHistoryLoadResult:
    """Closed history reconstruction result."""

    status: WorkflowHistoryLoadStatus
    stream_identity: str
    diagnostics: tuple[str, ...]
    history: WorkflowRuntimeHistory | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not WorkflowHistoryLoadStatus:
            raise TypeError("status must be WorkflowHistoryLoadStatus")
        if type(self.stream_identity) is not str or not self.stream_identity:
            raise ValueError("stream_identity must be nonempty")
        if type(self.diagnostics) is not tuple or any(
            type(value) is not str or not value for value in self.diagnostics
        ):
            raise TypeError("diagnostics must contain nonempty strings")
        if self.status is WorkflowHistoryLoadStatus.LOADED:
            if self.history is None:
                raise ValueError("loaded requires history")
        elif self.history is not None:
            raise ValueError("non-loaded result prohibits history")


@dataclass(frozen=True, slots=True)
class WorkflowEventAppendResult:
    """Closed runtime-event append result."""

    status: WorkflowEventAppendStatus
    event: WorkflowRuntimeEvent
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.status) is not WorkflowEventAppendStatus:
            raise TypeError("status must be WorkflowEventAppendStatus")
        if type(self.event) is not WorkflowRuntimeEvent:
            raise TypeError("event must be WorkflowRuntimeEvent")
        if type(self.diagnostics) is not tuple or any(
            type(value) is not str or not value for value in self.diagnostics
        ):
            raise TypeError("diagnostics must contain nonempty strings")


class WorkflowRuntimeRepository:
    """Persist and reconstruct immutable runtime events through one store."""

    def __init__(
        self,
        store: AtomicRevisionStore,
        serializer: WorkflowRuntimeEventSerializer | None = None,
    ) -> None:
        if not isinstance(store, AtomicRevisionStore):
            raise TypeError("store must satisfy AtomicRevisionStore")
        selected = serializer or WorkflowRuntimeEventSerializer()
        if type(selected) is not WorkflowRuntimeEventSerializer:
            raise TypeError("serializer must be WorkflowRuntimeEventSerializer")
        self._store = store
        self._serializer = selected

    def append(
        self,
        event: WorkflowRuntimeEvent,
        *,
        expected_event_identity: WorkflowRuntimeEventIdentity | None,
        idempotency_identity: str,
    ) -> WorkflowEventAppendResult:
        """Append one event with exact expected-head and idempotency binding."""
        if type(event) is not WorkflowRuntimeEvent:
            raise TypeError("event must be WorkflowRuntimeEvent")
        if (
            expected_event_identity is not None
            and type(expected_event_identity)
            is not WorkflowRuntimeEventIdentity
        ):
            raise TypeError(
                "expected_event_identity must be "
                "WorkflowRuntimeEventIdentity or None"
            )
        if event.predecessor_event_identity != expected_event_identity:
            raise ValueError("event predecessor must equal expected event")
        if type(idempotency_identity) is not str or not idempotency_identity:
            raise ValueError("idempotency_identity must be nonempty")
        payload = self._serializer.encode(event)
        revision = Revision(
            event.run_identity.value,
            event.identity.value,
            None
            if expected_event_identity is None
            else expected_event_identity.value,
            self._serializer.schema_identity,
            hashlib.sha256(payload).hexdigest(),
            payload,
        )
        result = self._store.commit(
            RevisionCommit(
                revision.predecessor_revision_identity,
                revision,
                idempotency_identity,
            )
        )
        status = {
            RevisionCommitStatus.COMMITTED: WorkflowEventAppendStatus.APPENDED,
            RevisionCommitStatus.IDEMPOTENT: (
                WorkflowEventAppendStatus.IDEMPOTENT
            ),
            RevisionCommitStatus.CONFLICT: WorkflowEventAppendStatus.CONFLICT,
            RevisionCommitStatus.INDETERMINATE: (
                WorkflowEventAppendStatus.INDETERMINATE
            ),
            RevisionCommitStatus.ERROR: WorkflowEventAppendStatus.ERROR,
        }[result.status]
        return WorkflowEventAppendResult(status, event, result.diagnostics)

    def load(self, stream_identity: str) -> WorkflowHistoryLoadResult:
        """Reconstruct and validate one complete predecessor chain."""
        if type(stream_identity) is not str or not stream_identity:
            raise ValueError("stream_identity must be nonempty")
        latest = self._store.read(
            RevisionReadRequest(
                _read_identity(stream_identity, "latest"),
                stream_identity,
                RevisionSelector.LATEST,
            )
        )
        if latest.status is RevisionReadStatus.ABSENT:
            return WorkflowHistoryLoadResult(
                WorkflowHistoryLoadStatus.ABSENT,
                stream_identity,
                latest.diagnostics,
            )
        failure = _load_failure(latest.status)
        if failure is not None:
            return WorkflowHistoryLoadResult(
                failure,
                stream_identity,
                latest.diagnostics,
            )
        assert latest.revision is not None
        reverse_events: list[WorkflowRuntimeEvent] = []
        revision = latest.revision
        visited: set[str] = set()
        while True:
            if revision.revision_identity in visited:
                return WorkflowHistoryLoadResult(
                    WorkflowHistoryLoadStatus.CORRUPT,
                    stream_identity,
                    ("runtime_event_cycle",),
                )
            if len(reverse_events) >= _MAX_EVENTS_PER_HISTORY:
                return WorkflowHistoryLoadResult(
                    WorkflowHistoryLoadStatus.CORRUPT,
                    stream_identity,
                    ("runtime_history_limit",),
                )
            visited.add(revision.revision_identity)
            if revision.schema_identity != self._serializer.schema_identity:
                return WorkflowHistoryLoadResult(
                    WorkflowHistoryLoadStatus.INCOMPATIBLE,
                    stream_identity,
                    ("runtime_event_schema",),
                )
            if (
                hashlib.sha256(revision.payload).hexdigest()
                != revision.content_identity
            ):
                return WorkflowHistoryLoadResult(
                    WorkflowHistoryLoadStatus.CORRUPT,
                    stream_identity,
                    ("runtime_event_content",),
                )
            try:
                event = self._serializer.decode(revision.payload)
            except TypeError, ValueError:
                return WorkflowHistoryLoadResult(
                    WorkflowHistoryLoadStatus.CORRUPT,
                    stream_identity,
                    ("runtime_event_decode",),
                )
            if (
                event.identity.value != revision.revision_identity
                or event.run_identity.value != stream_identity
                or (
                    None
                    if event.predecessor_event_identity is None
                    else event.predecessor_event_identity.value
                )
                != revision.predecessor_revision_identity
            ):
                return WorkflowHistoryLoadResult(
                    WorkflowHistoryLoadStatus.CORRUPT,
                    stream_identity,
                    ("runtime_event_binding",),
                )
            reverse_events.append(event)
            predecessor = revision.predecessor_revision_identity
            if predecessor is None:
                break
            prior = self._store.read(
                RevisionReadRequest(
                    _read_identity(stream_identity, predecessor),
                    stream_identity,
                    RevisionSelector.EXPLICIT,
                    predecessor,
                )
            )
            failure = _load_failure(prior.status)
            if failure is not None or prior.revision is None:
                return WorkflowHistoryLoadResult(
                    failure or WorkflowHistoryLoadStatus.CORRUPT,
                    stream_identity,
                    prior.diagnostics or ("runtime_predecessor_missing",),
                )
            revision = prior.revision
        try:
            history = WorkflowRuntimeHistory(
                stream_identity,
                tuple(reversed(reverse_events)),
            )
        except TypeError, ValueError:
            return WorkflowHistoryLoadResult(
                WorkflowHistoryLoadStatus.CORRUPT,
                stream_identity,
                ("runtime_history_invalid",),
            )
        return WorkflowHistoryLoadResult(
            WorkflowHistoryLoadStatus.LOADED,
            stream_identity,
            (),
            history,
        )


def _read_identity(stream_identity: str, selector: str) -> str:
    return hashlib.sha256(
        f"workflow-history-read:1\0{stream_identity}\0{selector}".encode()
    ).hexdigest()


def _load_failure(
    status: RevisionReadStatus,
) -> WorkflowHistoryLoadStatus | None:
    return {
        RevisionReadStatus.FOUND: None,
        RevisionReadStatus.ABSENT: WorkflowHistoryLoadStatus.CORRUPT,
        RevisionReadStatus.INCOMPATIBLE: WorkflowHistoryLoadStatus.INCOMPATIBLE,
        RevisionReadStatus.CORRUPT: WorkflowHistoryLoadStatus.CORRUPT,
        RevisionReadStatus.INDETERMINATE: (
            WorkflowHistoryLoadStatus.INDETERMINATE
        ),
        RevisionReadStatus.ERROR: WorkflowHistoryLoadStatus.ERROR,
    }[status]
