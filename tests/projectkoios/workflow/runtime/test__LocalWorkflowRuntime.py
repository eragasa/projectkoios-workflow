"""Software verification for the append-only local workflow runtime."""

from __future__ import annotations

from pathlib import Path

from _runtime_fixtures import runtime_fixture, transition_input
from projectkoios.workflow.core import WorkflowTransitionPreflightInput
from projectkoios.workflow.persistence import SQLiteAtomicRevisionStore
from projectkoios.workflow.runtime import (
    LocalWorkflowRuntime,
    WorkflowHistoryLoadStatus,
    WorkflowRuntimeActionStatus,
    WorkflowRuntimeEventKind,
    WorkflowRuntimeRepository,
)


def runtime(
    tmp_path: Path,
) -> tuple[LocalWorkflowRuntime, WorkflowRuntimeRepository]:
    repository = WorkflowRuntimeRepository(
        SQLiteAtomicRevisionStore(tmp_path / "private" / "runtime.sqlite3")
    )
    return LocalWorkflowRuntime(repository), repository


def test__local_runtime__retains_and_replays_course_candidate_transition(
    tmp_path: Path,
) -> None:
    selected, repository = runtime(tmp_path)
    fixture = runtime_fixture()
    candidate = transition_input(fixture)
    preflight = WorkflowTransitionPreflightInput(
        candidate.definition,
        candidate.run,
        candidate.prior_state,
        candidate.request,
    )

    started = selected.start(fixture.started)
    retained = selected.retain_request(preflight)
    transitioned = selected.record_transition(candidate)
    repeated = selected.record_transition(candidate)
    loaded = repository.load(fixture.started.run.identity.value)

    assert started.status is WorkflowRuntimeActionStatus.RECORDED
    assert retained.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.status is WorkflowRuntimeActionStatus.RECORDED
    assert transitioned.transition is not None
    assert repeated.status is WorkflowRuntimeActionStatus.IDEMPOTENT
    assert repeated.event == transitioned.event
    assert loaded.status is WorkflowHistoryLoadStatus.LOADED
    assert loaded.history is not None
    assert tuple(event.kind for event in loaded.history.events) == (
        WorkflowRuntimeEventKind.RUN_STARTED,
        WorkflowRuntimeEventKind.REQUEST_RETAINED,
        WorkflowRuntimeEventKind.TRANSITION_RECORDED,
    )
    assert tuple(event.ordinal for event in loaded.history.events) == (0, 1, 2)
    assert loaded.history.head.core_revision == 1
    assert loaded.history.head.reason_codes == ("applied",)
    assert all(
        "Courses/" not in reference.reference_identity
        for event in loaded.history.events
        for reference in event.evidence_references
    )


def test__local_runtime__records_same_revision_request_conflict(
    tmp_path: Path,
) -> None:
    selected, repository = runtime(tmp_path)
    fixture = runtime_fixture()
    first = transition_input(fixture, request_key="candidate:1")
    second = transition_input(fixture, request_key="candidate:2")
    selected.start(fixture.started)
    selected.retain_request(
        WorkflowTransitionPreflightInput(
            first.definition,
            first.run,
            first.prior_state,
            first.request,
        )
    )

    result = selected.retain_request(
        WorkflowTransitionPreflightInput(
            second.definition,
            second.run,
            second.prior_state,
            second.request,
        )
    )
    loaded = repository.load(fixture.started.run.identity.value)

    assert result.status is WorkflowRuntimeActionStatus.CONFLICT
    assert result.event is not None
    assert (
        result.event.kind is WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED
    )
    assert result.event.reason_codes == ("revision_reserved",)
    assert loaded.history is not None
    assert tuple(event.kind for event in loaded.history.events)[-1] is (
        WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED
    )
    assert selected.record_transition(second).status is (
        WorkflowRuntimeActionStatus.CONFLICT
    )


def test__local_runtime__rejects_changed_idempotency_reuse(
    tmp_path: Path,
) -> None:
    selected, repository = runtime(tmp_path)
    fixture = runtime_fixture()
    first = transition_input(fixture, request_key="candidate:stable")
    changed = transition_input(
        fixture,
        request_key="candidate:stable",
        proposal_identity="proposal-set:sha256:changed",
    )
    selected.start(fixture.started)
    retained = selected.retain_request(
        WorkflowTransitionPreflightInput(
            first.definition,
            first.run,
            first.prior_state,
            first.request,
        )
    )

    changed_preflight = WorkflowTransitionPreflightInput(
        changed.definition,
        changed.run,
        changed.prior_state,
        changed.request,
    )
    collision = selected.retain_request(changed_preflight)
    repeated = selected.retain_request(changed_preflight)
    loaded = repository.load(fixture.started.run.identity.value)

    assert retained.status is WorkflowRuntimeActionStatus.RECORDED
    assert collision.status is WorkflowRuntimeActionStatus.CONFLICT
    assert collision.event is not None
    assert collision.event.reason_codes == ("idempotency_collision",)
    assert repeated.status is WorkflowRuntimeActionStatus.CONFLICT
    assert repeated.event == collision.event
    assert loaded.history is not None
    assert len(loaded.history.events) == 3
    assert loaded.history.head.kind is (
        WorkflowRuntimeEventKind.REQUEST_CONFLICT_RECORDED
    )


def test__local_runtime__retains_structural_preflight_rejection(
    tmp_path: Path,
) -> None:
    selected, repository = runtime(tmp_path)
    fixture = runtime_fixture()
    stale = transition_input(fixture, expected_revision=1)
    selected.start(fixture.started)

    result = selected.retain_request(
        WorkflowTransitionPreflightInput(
            stale.definition,
            stale.run,
            stale.prior_state,
            stale.request,
        )
    )
    repeated = selected.retain_request(
        WorkflowTransitionPreflightInput(
            stale.definition,
            stale.run,
            stale.prior_state,
            stale.request,
        )
    )
    loaded = repository.load(fixture.started.run.identity.value)

    assert result.status is WorkflowRuntimeActionStatus.REJECTED
    assert result.validation is not None
    assert result.event is not None
    assert result.event.kind is WorkflowRuntimeEventKind.PREFLIGHT_REJECTED
    assert result.event.reason_codes == ("revision_conflict",)
    assert repeated.status is WorkflowRuntimeActionStatus.REJECTED
    assert repeated.event == result.event
    assert loaded.history is not None
    assert loaded.history.head.core_revision == 0


def test__local_runtime__start_is_idempotent_across_reopen(
    tmp_path: Path,
) -> None:
    first, _ = runtime(tmp_path)
    fixture = runtime_fixture()
    recorded = first.start(fixture.started)
    reopened, repository = runtime(tmp_path)

    replay = reopened.start(fixture.started)
    loaded = repository.load(fixture.started.run.identity.value)

    assert recorded.status is WorkflowRuntimeActionStatus.RECORDED
    assert replay.status is WorkflowRuntimeActionStatus.IDEMPOTENT
    assert replay.event == recorded.event
    assert loaded.history is not None
    assert len(loaded.history.events) == 1
