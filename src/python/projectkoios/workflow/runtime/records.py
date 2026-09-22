"""Immutable payload-free records for the local workflow runtime."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum

from projectkoios.workflow.core import (
    WorkflowOperationIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    WorkflowTransitionRequestIdentity,
)

WORKFLOW_RUNTIME_CONTRACT_VERSION = "0.1.0"
WORKFLOW_RUNTIME_IMPLEMENTATION_IDENTITY = (
    "projectkoios-workflow.local-runtime:0.1.0"
)
_MAX_REFERENCES = 256
_MAX_REASONS = 64
_MAX_TEXT = 512
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,511}$", re.ASCII)


def _identity(value: object, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a built-in str")
    if _IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"{field} has an invalid identity grammar")
    return value


def _content_identity(domain: str, parts: object) -> str:
    payload = json.dumps(
        {"domain": domain, "parts": parts},
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class WorkflowRuntimeEventIdentity:
    """Nominal identity of one immutable runtime event."""

    value: str

    def __post_init__(self) -> None:
        if (
            type(self.value) is not str
            or re.fullmatch(r"[0-9a-f]{64}", self.value) is None
        ):
            raise ValueError("runtime event identity must be 64 lowercase hex")


@dataclass(frozen=True, slots=True)
class WorkflowOccurrenceIdentity:
    """Nominal identity of one revision-bound transition occurrence."""

    value: str

    def __post_init__(self) -> None:
        if (
            type(self.value) is not str
            or re.fullmatch(r"[0-9a-f]{64}", self.value) is None
        ):
            raise ValueError("occurrence identity must be 64 lowercase hex")

    @classmethod
    def create(
        cls,
        *,
        run_identity: WorkflowRunIdentity,
        state_identity: WorkflowStateIdentity,
        revision: int,
        request_identity: WorkflowTransitionRequestIdentity,
    ) -> WorkflowOccurrenceIdentity:
        """Derive one occurrence from exact immutable core identities."""
        if type(run_identity) is not WorkflowRunIdentity:
            raise TypeError("run_identity must be WorkflowRunIdentity")
        if type(state_identity) is not WorkflowStateIdentity:
            raise TypeError("state_identity must be WorkflowStateIdentity")
        if type(revision) is not int or revision < 0:
            raise ValueError("revision must be a nonnegative built-in int")
        if type(request_identity) is not WorkflowTransitionRequestIdentity:
            raise TypeError(
                "request_identity must be WorkflowTransitionRequestIdentity"
            )
        return cls(
            _content_identity(
                "workflow-occurrence:1",
                [
                    run_identity.value,
                    state_identity.value,
                    revision,
                    request_identity.value,
                    WORKFLOW_RUNTIME_CONTRACT_VERSION,
                ],
            )
        )


@dataclass(frozen=True, slots=True, order=True)
class WorkflowRuntimeEvidenceReference:
    """Compact typed reference to evidence retained by another owner."""

    reference_kind: str
    reference_identity: str

    def __post_init__(self) -> None:
        _identity(self.reference_kind, "reference_kind")
        if type(self.reference_identity) is not str:
            raise TypeError("reference_identity must be a built-in str")
        value = self.reference_identity
        if not value or len(value) > _MAX_TEXT:
            raise ValueError("reference_identity must be nonempty and bounded")
        if any(
            ord(character) < 32 or ord(character) == 127 for character in value
        ):
            raise ValueError(
                "reference_identity must exclude control characters"
            )
        if (
            value.startswith(("/", "~/", "\\", "file:"))
            or re.match(r"^[A-Za-z]:[\\/]", value) is not None
        ):
            raise ValueError("reference_identity must exclude machine paths")


class WorkflowRuntimeEventKind(StrEnum):
    """Initial closed semantic event vocabulary."""

    RUN_STARTED = "run_started"
    REQUEST_RETAINED = "request_retained"
    REQUEST_CONFLICT_RECORDED = "request_conflict_recorded"
    PREFLIGHT_REJECTED = "preflight_rejected"
    PLAN_RECORDED = "plan_recorded"
    PLAN_DISABLED = "plan_disabled"
    PLAN_REJECTED = "plan_rejected"
    TRANSITION_RECORDED = "transition_recorded"
    TERMINAL_FAILURE_RECORDED = "terminal_failure_recorded"


@dataclass(frozen=True, slots=True)
class WorkflowRuntimeEvent:
    """One content-identified event in an authoritative per-run chain."""

    identity: WorkflowRuntimeEventIdentity
    kind: WorkflowRuntimeEventKind
    run_identity: WorkflowRunIdentity
    ordinal: int
    predecessor_event_identity: WorkflowRuntimeEventIdentity | None
    core_revision: int
    core_state_identity: WorkflowStateIdentity
    occurrence_identity: WorkflowOccurrenceIdentity | None
    request_identity: WorkflowTransitionRequestIdentity | None
    operation_identity: WorkflowOperationIdentity | None
    evidence_references: tuple[WorkflowRuntimeEvidenceReference, ...]
    reason_codes: tuple[str, ...]
    contract_version: str = WORKFLOW_RUNTIME_CONTRACT_VERSION
    producer_implementation: str = WORKFLOW_RUNTIME_IMPLEMENTATION_IDENTITY

    @classmethod
    def create(
        cls,
        *,
        kind: WorkflowRuntimeEventKind,
        run_identity: WorkflowRunIdentity,
        ordinal: int,
        predecessor_event_identity: WorkflowRuntimeEventIdentity | None,
        core_revision: int,
        core_state_identity: WorkflowStateIdentity,
        occurrence_identity: WorkflowOccurrenceIdentity | None = None,
        request_identity: WorkflowTransitionRequestIdentity | None = None,
        operation_identity: WorkflowOperationIdentity | None = None,
        evidence_references: tuple[WorkflowRuntimeEvidenceReference, ...] = (),
        reason_codes: tuple[str, ...] = (),
    ) -> WorkflowRuntimeEvent:
        """Construct a content-identified event."""
        evidence = _evidence(evidence_references)
        reasons = _reasons(reason_codes)
        parts = _event_parts(
            kind,
            run_identity,
            ordinal,
            predecessor_event_identity,
            core_revision,
            core_state_identity,
            occurrence_identity,
            request_identity,
            operation_identity,
            evidence,
            reasons,
        )
        return cls(
            WorkflowRuntimeEventIdentity(
                _content_identity("workflow-runtime-event:1", parts)
            ),
            kind,
            run_identity,
            ordinal,
            predecessor_event_identity,
            core_revision,
            core_state_identity,
            occurrence_identity,
            request_identity,
            operation_identity,
            evidence,
            reasons,
        )

    def __post_init__(self) -> None:
        if type(self.identity) is not WorkflowRuntimeEventIdentity:
            raise TypeError("identity must be WorkflowRuntimeEventIdentity")
        if type(self.kind) is not WorkflowRuntimeEventKind:
            raise TypeError("kind must be WorkflowRuntimeEventKind")
        if type(self.run_identity) is not WorkflowRunIdentity:
            raise TypeError("run_identity must be WorkflowRunIdentity")
        for name in ("ordinal", "core_revision"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative built-in int")
        if self.ordinal == 0:
            if self.predecessor_event_identity is not None:
                raise ValueError("genesis event cannot have a predecessor")
            if self.kind is not WorkflowRuntimeEventKind.RUN_STARTED:
                raise ValueError("genesis event must be run_started")
        elif self.predecessor_event_identity is None:
            raise ValueError("non-genesis event requires a predecessor")
        if type(self.core_state_identity) is not WorkflowStateIdentity:
            raise TypeError("core_state_identity must be WorkflowStateIdentity")
        if (
            self.occurrence_identity is not None
            and type(self.occurrence_identity) is not WorkflowOccurrenceIdentity
        ):
            raise TypeError(
                "occurrence_identity must be WorkflowOccurrenceIdentity or None"
            )
        if (
            self.request_identity is not None
            and type(self.request_identity)
            is not WorkflowTransitionRequestIdentity
        ):
            raise TypeError(
                "request_identity must be "
                "WorkflowTransitionRequestIdentity or None"
            )
        if (
            self.operation_identity is not None
            and type(self.operation_identity) is not WorkflowOperationIdentity
        ):
            raise TypeError(
                "operation_identity must be WorkflowOperationIdentity or None"
            )
        if _evidence(self.evidence_references) != self.evidence_references:
            raise ValueError("evidence references must be canonical")
        if _reasons(self.reason_codes) != self.reason_codes:
            raise ValueError("reason codes must be canonical")
        if self.contract_version != WORKFLOW_RUNTIME_CONTRACT_VERSION:
            raise ValueError("unsupported workflow runtime contract version")
        if self.producer_implementation != (
            WORKFLOW_RUNTIME_IMPLEMENTATION_IDENTITY
        ):
            raise ValueError("unsupported runtime producer implementation")
        expected = WorkflowRuntimeEventIdentity(
            _content_identity(
                "workflow-runtime-event:1",
                _event_parts(
                    self.kind,
                    self.run_identity,
                    self.ordinal,
                    self.predecessor_event_identity,
                    self.core_revision,
                    self.core_state_identity,
                    self.occurrence_identity,
                    self.request_identity,
                    self.operation_identity,
                    self.evidence_references,
                    self.reason_codes,
                ),
            )
        )
        if self.identity != expected:
            raise ValueError("runtime event identity is inconsistent")


def _evidence(
    values: tuple[WorkflowRuntimeEvidenceReference, ...],
) -> tuple[WorkflowRuntimeEvidenceReference, ...]:
    if type(values) is not tuple:
        raise TypeError("evidence_references must be a tuple")
    if len(values) > _MAX_REFERENCES:
        raise ValueError("evidence_references exceed their bound")
    if any(
        type(value) is not WorkflowRuntimeEvidenceReference for value in values
    ):
        raise TypeError(
            "evidence_references must contain WorkflowRuntimeEvidenceReference"
        )
    canonical = tuple(sorted(set(values)))
    return canonical


def _reasons(values: tuple[str, ...]) -> tuple[str, ...]:
    if type(values) is not tuple:
        raise TypeError("reason_codes must be a tuple")
    if len(values) > _MAX_REASONS:
        raise ValueError("reason_codes exceed their bound")
    for value in values:
        _identity(value, "reason_code")
        if len(value) > _MAX_TEXT:
            raise ValueError("reason_code exceeds its bound")
    return tuple(sorted(set(values)))


def _event_parts(
    kind: WorkflowRuntimeEventKind,
    run_identity: WorkflowRunIdentity,
    ordinal: int,
    predecessor: WorkflowRuntimeEventIdentity | None,
    core_revision: int,
    state_identity: WorkflowStateIdentity,
    occurrence: WorkflowOccurrenceIdentity | None,
    request: WorkflowTransitionRequestIdentity | None,
    operation: WorkflowOperationIdentity | None,
    evidence: tuple[WorkflowRuntimeEvidenceReference, ...],
    reasons: tuple[str, ...],
) -> list[object]:
    return [
        kind.value,
        run_identity.value,
        ordinal,
        None if predecessor is None else predecessor.value,
        core_revision,
        state_identity.value,
        None if occurrence is None else occurrence.value,
        None if request is None else request.value,
        None if operation is None else operation.value,
        [
            [value.reference_kind, value.reference_identity]
            for value in evidence
        ],
        list(reasons),
        WORKFLOW_RUNTIME_CONTRACT_VERSION,
        WORKFLOW_RUNTIME_IMPLEMENTATION_IDENTITY,
    ]
