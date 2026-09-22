"""Bounded local runtime orchestration around the pure workflow core."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from projectkoios.workflow.core import (
    WorkflowOperationIdentity,
    WorkflowRunStartResult,
    WorkflowStateIdentity,
    WorkflowTransitionExecution,
    WorkflowTransitionInput,
    WorkflowTransitionPreflightInput,
    WorkflowTransitionProcessor,
    WorkflowTransitionRequestIdentity,
    WorkflowTransitionValidator,
    WorkflowValidationResult,
)

from .records import (
    WorkflowOccurrenceIdentity,
    WorkflowRuntimeEvent,
    WorkflowRuntimeEventKind,
    WorkflowRuntimeEvidenceReference,
)
from .repository import (
    WorkflowEventAppendStatus,
    WorkflowHistoryLoadStatus,
    WorkflowRuntimeHistory,
    WorkflowRuntimeRepository,
)


class WorkflowRuntimeActionStatus(StrEnum):
    """Closed result of one local runtime action."""

    RECORDED = "recorded"
    IDEMPOTENT = "idempotent"
    REJECTED = "rejected"
    CONFLICT = "conflict"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class WorkflowRuntimeActionResult:
    """Represent one runtime action without hiding persistence uncertainty."""

    status: WorkflowRuntimeActionStatus
    event: WorkflowRuntimeEvent | None
    diagnostics: tuple[str, ...]
    validation: WorkflowValidationResult | None = None
    transition: WorkflowTransitionExecution | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not WorkflowRuntimeActionStatus:
            raise TypeError("status must be WorkflowRuntimeActionStatus")
        if (
            self.event is not None
            and type(self.event) is not WorkflowRuntimeEvent
        ):
            raise TypeError("event must be WorkflowRuntimeEvent or None")
        if type(self.diagnostics) is not tuple or any(
            type(value) is not str or not value for value in self.diagnostics
        ):
            raise TypeError("diagnostics must contain nonempty strings")
        if (
            self.validation is not None
            and type(self.validation) is not WorkflowValidationResult
        ):
            raise TypeError(
                "validation must be WorkflowValidationResult or None"
            )
        if (
            self.transition is not None
            and type(self.transition) is not WorkflowTransitionExecution
        ):
            raise TypeError(
                "transition must be WorkflowTransitionExecution or None"
            )
        if (
            self.status
            in {
                WorkflowRuntimeActionStatus.RECORDED,
                WorkflowRuntimeActionStatus.IDEMPOTENT,
                WorkflowRuntimeActionStatus.REJECTED,
            }
            and self.event is None
        ):
            raise ValueError(f"{self.status.value} requires an event")


class LocalWorkflowRuntime:
    """Retain run, request, and pure transition evidence without dispatch."""

    def __init__(self, repository: WorkflowRuntimeRepository) -> None:
        if type(repository) is not WorkflowRuntimeRepository:
            raise TypeError("repository must be WorkflowRuntimeRepository")
        self._repository = repository
        self._validator = WorkflowTransitionValidator()
        self._processor = WorkflowTransitionProcessor()

    def start(
        self, started: WorkflowRunStartResult
    ) -> WorkflowRuntimeActionResult:
        """Record one exact revision-zero run or return its retained genesis."""
        if type(started) is not WorkflowRunStartResult:
            raise TypeError("started must be WorkflowRunStartResult")
        evidence = [
            WorkflowRuntimeEvidenceReference(
                "workflow-definition",
                started.run.definition_identity.value,
            ),
            WorkflowRuntimeEvidenceReference(
                "workflow-subject",
                started.run.subject_identity.value,
            ),
        ]
        evidence.extend(
            WorkflowRuntimeEvidenceReference(
                "artifact-reference", value.identity.value
            )
            for value in started.run.artifact_references
        )
        evidence.extend(
            WorkflowRuntimeEvidenceReference(
                "decision-reference", value.identity.value
            )
            for value in started.run.decision_references
        )
        if started.run.parent_run_identity is not None:
            evidence.append(
                WorkflowRuntimeEvidenceReference(
                    "parent-run", started.run.parent_run_identity.value
                )
            )
        if started.run.predecessor_run_identity is not None:
            evidence.append(
                WorkflowRuntimeEvidenceReference(
                    "predecessor-run",
                    started.run.predecessor_run_identity.value,
                )
            )
        event = WorkflowRuntimeEvent.create(
            kind=WorkflowRuntimeEventKind.RUN_STARTED,
            run_identity=started.run.identity,
            ordinal=0,
            predecessor_event_identity=None,
            core_revision=started.run.revision,
            core_state_identity=started.state.identity,
            evidence_references=tuple(evidence),
        )
        loaded = self._repository.load(started.run.identity.value)
        if loaded.status is WorkflowHistoryLoadStatus.LOADED:
            assert loaded.history is not None
            genesis = loaded.history.events[0]
            if genesis == event:
                return WorkflowRuntimeActionResult(
                    WorkflowRuntimeActionStatus.IDEMPOTENT,
                    genesis,
                    (),
                )
            return WorkflowRuntimeActionResult(
                WorkflowRuntimeActionStatus.CONFLICT,
                None,
                ("run_identity_collision",),
            )
        if loaded.status is not WorkflowHistoryLoadStatus.ABSENT:
            return _load_failure_result(loaded.status, loaded.diagnostics)
        return _append_result(
            self._repository.append(
                event,
                expected_event_identity=None,
                idempotency_identity=f"runtime-start:{event.identity.value}",
            )
        )

    def retain_request(
        self,
        preflight: WorkflowTransitionPreflightInput,
    ) -> WorkflowRuntimeActionResult:
        """Preflight and reserve one request at one exact core revision."""
        if type(preflight) is not WorkflowTransitionPreflightInput:
            raise TypeError(
                "preflight must be WorkflowTransitionPreflightInput"
            )
        loaded = self._repository.load(preflight.run.identity.value)
        if loaded.status is not WorkflowHistoryLoadStatus.LOADED:
            return _load_failure_result(loaded.status, loaded.diagnostics)
        assert loaded.history is not None
        history = loaded.history
        if (
            history.head.core_revision != preflight.run.revision
            or history.head.core_state_identity
            != preflight.prior_state.identity
        ):
            return WorkflowRuntimeActionResult(
                WorkflowRuntimeActionStatus.CONFLICT,
                None,
                ("runtime_head_core_mismatch",),
            )
        existing = _request_event(history, preflight.request.identity.value)
        if existing is not None:
            status = (
                WorkflowRuntimeActionStatus.REJECTED
                if existing.kind is WorkflowRuntimeEventKind.PREFLIGHT_REJECTED
                else WorkflowRuntimeActionStatus.CONFLICT
                if existing.kind
                is WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED
                else WorkflowRuntimeActionStatus.IDEMPOTENT
            )
            return WorkflowRuntimeActionResult(status, existing, ())
        idempotency_owner = _idempotency_owner(
            history,
            preflight.request.idempotency_identity.value,
        )
        if idempotency_owner is not None:
            assert idempotency_owner.request_identity is not None
            event = _next_event(
                history,
                kind=WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED,
                core_revision=preflight.run.revision,
                core_state_identity=preflight.prior_state.identity,
                occurrence_identity=WorkflowOccurrenceIdentity.create(
                    run_identity=preflight.run.identity,
                    state_identity=preflight.prior_state.identity,
                    revision=preflight.run.revision,
                    request_identity=preflight.request.identity,
                ),
                request_identity=preflight.request.identity,
                operation_identity=preflight.request.operation_identity,
                evidence_references=(
                    WorkflowRuntimeEvidenceReference(
                        "idempotency-owner-request",
                        idempotency_owner.request_identity.value,
                    ),
                    WorkflowRuntimeEvidenceReference(
                        "request-idempotency",
                        preflight.request.idempotency_identity.value,
                    ),
                ),
                reason_codes=("idempotency_collision",),
            )
            appended = self._repository.append(
                event,
                expected_event_identity=history.head.identity,
                idempotency_identity=(
                    f"runtime-idempotency-conflict:{event.identity.value}"
                ),
            )
            result = _append_result(appended)
            if result.status is WorkflowRuntimeActionStatus.RECORDED:
                return WorkflowRuntimeActionResult(
                    WorkflowRuntimeActionStatus.CONFLICT,
                    result.event,
                    result.diagnostics,
                )
            return result
        occurrence = WorkflowOccurrenceIdentity.create(
            run_identity=preflight.run.identity,
            state_identity=preflight.prior_state.identity,
            revision=preflight.run.revision,
            request_identity=preflight.request.identity,
        )
        active = _active_occurrence(history, preflight.run.revision)
        if active is not None:
            assert active.occurrence_identity is not None
            assert active.request_identity is not None
            event = _next_event(
                history,
                kind=WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED,
                core_revision=preflight.run.revision,
                core_state_identity=preflight.prior_state.identity,
                occurrence_identity=occurrence,
                request_identity=preflight.request.identity,
                operation_identity=preflight.request.operation_identity,
                evidence_references=(
                    WorkflowRuntimeEvidenceReference(
                        "active-occurrence", active.occurrence_identity.value
                    ),
                    WorkflowRuntimeEvidenceReference(
                        "active-request", active.request_identity.value
                    ),
                ),
                reason_codes=("revision_reserved",),
            )
            appended = self._repository.append(
                event,
                expected_event_identity=history.head.identity,
                idempotency_identity=f"runtime-conflict:{event.identity.value}",
            )
            result = _append_result(appended)
            if result.status is WorkflowRuntimeActionStatus.RECORDED:
                return WorkflowRuntimeActionResult(
                    WorkflowRuntimeActionStatus.CONFLICT,
                    result.event,
                    result.diagnostics,
                )
            return result
        validation = self._validator.execute(preflight)
        if validation.findings:
            event = _next_event(
                history,
                kind=WorkflowRuntimeEventKind.PREFLIGHT_REJECTED,
                core_revision=preflight.run.revision,
                core_state_identity=preflight.prior_state.identity,
                occurrence_identity=occurrence,
                request_identity=preflight.request.identity,
                operation_identity=preflight.request.operation_identity,
                evidence_references=(
                    WorkflowRuntimeEvidenceReference(
                        "request-idempotency",
                        preflight.request.idempotency_identity.value,
                    ),
                    WorkflowRuntimeEvidenceReference(
                        "workflow-validation", validation.identity.value
                    ),
                ),
                reason_codes=tuple(
                    finding.code.value for finding in validation.findings
                ),
            )
            appended = self._repository.append(
                event,
                expected_event_identity=history.head.identity,
                idempotency_identity=f"runtime-preflight:{event.identity.value}",
            )
            result = _append_result(appended, validation=validation)
            if result.status is WorkflowRuntimeActionStatus.RECORDED:
                return WorkflowRuntimeActionResult(
                    WorkflowRuntimeActionStatus.REJECTED,
                    result.event,
                    result.diagnostics,
                    validation,
                )
            return result
        event = _next_event(
            history,
            kind=WorkflowRuntimeEventKind.REQUEST_RETAINED,
            core_revision=preflight.run.revision,
            core_state_identity=preflight.prior_state.identity,
            occurrence_identity=occurrence,
            request_identity=preflight.request.identity,
            operation_identity=preflight.request.operation_identity,
            evidence_references=(
                WorkflowRuntimeEvidenceReference(
                    "authority-reference",
                    preflight.request.authority_reference.identity.value,
                ),
                WorkflowRuntimeEvidenceReference(
                    "request-idempotency",
                    preflight.request.idempotency_identity.value,
                ),
                WorkflowRuntimeEvidenceReference(
                    "workflow-validation", validation.identity.value
                ),
            ),
        )
        return _append_result(
            self._repository.append(
                event,
                expected_event_identity=history.head.identity,
                idempotency_identity=f"runtime-request:{event.identity.value}",
            ),
            validation=validation,
        )

    def record_transition(
        self,
        transition_input: WorkflowTransitionInput,
    ) -> WorkflowRuntimeActionResult:
        """Process and retain one pure adapter result for a reserved request."""
        if type(transition_input) is not WorkflowTransitionInput:
            raise TypeError("transition_input must be WorkflowTransitionInput")
        loaded = self._repository.load(transition_input.run.identity.value)
        if loaded.status is not WorkflowHistoryLoadStatus.LOADED:
            return _load_failure_result(loaded.status, loaded.diagnostics)
        assert loaded.history is not None
        history = loaded.history
        request = transition_input.request
        prior = transition_input.prior_state
        retained = _retained_occurrence(history, request.identity.value)
        if retained is None:
            return WorkflowRuntimeActionResult(
                WorkflowRuntimeActionStatus.CONFLICT,
                None,
                ("request_not_reserved",),
            )
        existing = _transition_event(history, request.identity.value)
        if existing is not None:
            return WorkflowRuntimeActionResult(
                WorkflowRuntimeActionStatus.IDEMPOTENT,
                existing,
                (),
            )
        if (
            history.head.core_revision != transition_input.run.revision
            or history.head.core_state_identity != prior.identity
        ):
            return WorkflowRuntimeActionResult(
                WorkflowRuntimeActionStatus.CONFLICT,
                None,
                ("runtime_head_core_mismatch",),
            )
        transition = self._processor.execute(transition_input)
        successor = transition.outcome.successor_run
        successor_state = transition.outcome.successor_state
        core_revision = (
            transition_input.run.revision
            if successor is None
            else successor.revision
        )
        core_state = (
            prior.identity
            if successor_state is None
            else successor_state.identity
        )
        evidence = [
            WorkflowRuntimeEvidenceReference(
                "transition-outcome", transition.outcome.identity.value
            ),
            WorkflowRuntimeEvidenceReference(
                "transition-audit", transition.audit_event.identity.value
            ),
            WorkflowRuntimeEvidenceReference(
                "workflow-validation",
                transition.outcome.validation.identity.value,
            ),
        ]
        if transition.outcome.adapter_evidence_identity is not None:
            evidence.append(
                WorkflowRuntimeEvidenceReference(
                    "adapter-evidence",
                    transition.outcome.adapter_evidence_identity.value,
                )
            )
        if transition.outcome.infrastructure_failure_identity is not None:
            evidence.append(
                WorkflowRuntimeEvidenceReference(
                    "infrastructure-failure",
                    transition.outcome.infrastructure_failure_identity.value,
                )
            )
        event = _next_event(
            history,
            kind=WorkflowRuntimeEventKind.TRANSITION_RECORDED,
            core_revision=core_revision,
            core_state_identity=core_state,
            occurrence_identity=retained.occurrence_identity,
            request_identity=request.identity,
            operation_identity=request.operation_identity,
            evidence_references=tuple(evidence),
            reason_codes=(transition.outcome.kind.value,),
        )
        return _append_result(
            self._repository.append(
                event,
                expected_event_identity=history.head.identity,
                idempotency_identity=f"runtime-transition:{event.identity.value}",
            ),
            validation=transition.outcome.validation,
            transition=transition,
        )


def _next_event(
    history: WorkflowRuntimeHistory,
    *,
    kind: WorkflowRuntimeEventKind,
    core_revision: int,
    core_state_identity: WorkflowStateIdentity,
    occurrence_identity: WorkflowOccurrenceIdentity | None,
    request_identity: WorkflowTransitionRequestIdentity | None,
    operation_identity: WorkflowOperationIdentity | None,
    evidence_references: tuple[WorkflowRuntimeEvidenceReference, ...],
    reason_codes: tuple[str, ...] = (),
) -> WorkflowRuntimeEvent:
    return WorkflowRuntimeEvent.create(
        kind=kind,
        run_identity=history.head.run_identity,
        ordinal=history.head.ordinal + 1,
        predecessor_event_identity=history.head.identity,
        core_revision=core_revision,
        core_state_identity=core_state_identity,
        occurrence_identity=occurrence_identity,
        request_identity=request_identity,
        operation_identity=operation_identity,
        evidence_references=evidence_references,
        reason_codes=reason_codes,
    )


def _request_event(
    history: WorkflowRuntimeHistory,
    request_identity: str,
) -> WorkflowRuntimeEvent | None:
    return next(
        (
            event
            for event in history.events
            if event.request_identity is not None
            and event.request_identity.value == request_identity
            and event.kind
            in {
                WorkflowRuntimeEventKind.REQUEST_RETAINED,
                WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED,
                WorkflowRuntimeEventKind.PREFLIGHT_REJECTED,
            }
        ),
        None,
    )


def _idempotency_owner(
    history: WorkflowRuntimeHistory,
    idempotency_identity: str,
) -> WorkflowRuntimeEvent | None:
    return next(
        (
            event
            for event in history.events
            if event.kind
            in {
                WorkflowRuntimeEventKind.REQUEST_RETAINED,
                WorkflowRuntimeEventKind.PREFLIGHT_REJECTED,
            }
            and any(
                reference.reference_kind == "request-idempotency"
                and reference.reference_identity == idempotency_identity
                for reference in event.evidence_references
            )
        ),
        None,
    )


def _active_occurrence(
    history: WorkflowRuntimeHistory,
    revision: int,
) -> WorkflowRuntimeEvent | None:
    retained = [
        event
        for event in history.events
        if event.kind is WorkflowRuntimeEventKind.REQUEST_RETAINED
        and event.core_revision == revision
    ]
    for event in reversed(retained):
        assert event.occurrence_identity is not None
        completed = any(
            later.kind is WorkflowRuntimeEventKind.TRANSITION_RECORDED
            and later.occurrence_identity == event.occurrence_identity
            for later in history.events[event.ordinal + 1 :]
        )
        if not completed:
            return event
    return None


def _retained_occurrence(
    history: WorkflowRuntimeHistory,
    request_identity: str,
) -> WorkflowRuntimeEvent | None:
    return next(
        (
            event
            for event in history.events
            if event.kind is WorkflowRuntimeEventKind.REQUEST_RETAINED
            and event.request_identity is not None
            and event.request_identity.value == request_identity
        ),
        None,
    )


def _transition_event(
    history: WorkflowRuntimeHistory,
    request_identity: str,
) -> WorkflowRuntimeEvent | None:
    return next(
        (
            event
            for event in history.events
            if event.kind is WorkflowRuntimeEventKind.TRANSITION_RECORDED
            and event.request_identity is not None
            and event.request_identity.value == request_identity
        ),
        None,
    )


def _append_result(
    result: object,
    *,
    validation: WorkflowValidationResult | None = None,
    transition: WorkflowTransitionExecution | None = None,
) -> WorkflowRuntimeActionResult:
    from .repository import WorkflowEventAppendResult

    if type(result) is not WorkflowEventAppendResult:
        raise TypeError("result must be WorkflowEventAppendResult")
    status = {
        WorkflowEventAppendStatus.APPENDED: (
            WorkflowRuntimeActionStatus.RECORDED
        ),
        WorkflowEventAppendStatus.IDEMPOTENT: (
            WorkflowRuntimeActionStatus.IDEMPOTENT
        ),
        WorkflowEventAppendStatus.CONFLICT: (
            WorkflowRuntimeActionStatus.CONFLICT
        ),
        WorkflowEventAppendStatus.INDETERMINATE: (
            WorkflowRuntimeActionStatus.INDETERMINATE
        ),
        WorkflowEventAppendStatus.ERROR: WorkflowRuntimeActionStatus.ERROR,
    }[result.status]
    event = (
        result.event
        if result.status
        in {
            WorkflowEventAppendStatus.APPENDED,
            WorkflowEventAppendStatus.IDEMPOTENT,
        }
        else None
    )
    return WorkflowRuntimeActionResult(
        status,
        event,
        result.diagnostics,
        validation,
        transition,
    )


def _load_failure_result(
    status: WorkflowHistoryLoadStatus,
    diagnostics: tuple[str, ...],
) -> WorkflowRuntimeActionResult:
    mapped = {
        WorkflowHistoryLoadStatus.ABSENT: WorkflowRuntimeActionStatus.CONFLICT,
        WorkflowHistoryLoadStatus.INCOMPATIBLE: (
            WorkflowRuntimeActionStatus.ERROR
        ),
        WorkflowHistoryLoadStatus.CORRUPT: WorkflowRuntimeActionStatus.ERROR,
        WorkflowHistoryLoadStatus.INDETERMINATE: (
            WorkflowRuntimeActionStatus.INDETERMINATE
        ),
        WorkflowHistoryLoadStatus.ERROR: WorkflowRuntimeActionStatus.ERROR,
    }
    if status is WorkflowHistoryLoadStatus.LOADED:
        raise ValueError("loaded is not a failure")
    return WorkflowRuntimeActionResult(
        mapped[status],
        None,
        diagnostics or ("runtime_history_unavailable",),
    )
