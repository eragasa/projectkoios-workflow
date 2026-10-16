"""Bounded structural reconstruction of committed pure-action safety state."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from _durable_cpn_replay_fixtures import _durable_orchestration
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommitService,
    ExperimentalWorkflowPureActionDurableCpnCommitService,
    ExperimentalWorkflowPureActionSafetyStateReadStatus,
    ExperimentalWorkflowPureActionSafetyStateReplayService,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitStatus,
)


def _durably_commit(tmp_path: Path):  # type: ignore[no-untyped-def]
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    committed = ExperimentalWorkflowPureActionDurableCpnCommitService(
        reservation_service,
        repository,
    ).execute(
        authorized_inputs=fixture.invocation_fixture.authorized,
        reservation_result=reservation_result,
        cpn_plan=plan,
        invocation_outcome=fixture.invocation,
        firing_outcome=fixture.firing,
    )
    assert (
        committed.status is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )
    assert committed.commit is not None
    reservation = reservation_result.reservation
    assert reservation is not None
    return fixture, repository, reservation, committed.commit


def test_reconstructs_one_correlated_committed_safety_snapshot(
    tmp_path: Path,
) -> None:
    fixture, repository, reservation, commit = _durably_commit(tmp_path)
    fixture.invocation_fixture.source_repository._raise_error = True
    owner_calls = fixture.invocation_fixture.firer.calls

    result = ExperimentalWorkflowPureActionSafetyStateReplayService(
        repository
    ).execute(reservation.identity)

    assert (
        result.status
        is ExperimentalWorkflowPureActionSafetyStateReadStatus.FOUND
    )
    assert result.snapshot is not None
    assert (
        result.snapshot.committed_snapshot.record.commit_identity
        == commit.identity
    )
    assert result.snapshot.lifecycle[0].reservation == reservation
    assert (
        result.snapshot.initial_predecessor.marking_identity
        == commit.predecessor_marking_identity
    )
    assert (
        result.snapshot.current_predecessor.marking_identity
        == commit.successor_marking_identity
    )
    assert (
        result.snapshot.current_predecessor.revision
        == commit.successor_revision
    )
    assert (
        result.snapshot.predecessor_marking.identity.value
        == commit.predecessor_marking_identity.value
    )
    assert (
        result.snapshot.successor_marking.identity.value
        == commit.successor_marking_identity.value
    )
    assert fixture.invocation_fixture.firer.calls == owner_calls == 1


def test_active_and_compact_only_histories_are_closed_nonfound_outcomes(
    tmp_path: Path,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    reservation = reservation_result.reservation
    assert reservation is not None
    active = ExperimentalWorkflowPureActionSafetyStateReplayService(
        repository
    ).execute(reservation.identity)
    assert (
        active.status
        is ExperimentalWorkflowPureActionSafetyStateReadStatus.ABSENT
    )

    legacy = ExperimentalWorkflowPureActionCommitService(
        reservation_service
    ).execute(
        authorized_inputs=fixture.invocation_fixture.authorized,
        reservation_result=reservation_result,
        cpn_plan=plan,
        invocation_outcome=fixture.invocation,
        firing_outcome=fixture.firing,
    )
    assert legacy.status is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    partial = ExperimentalWorkflowPureActionSafetyStateReplayService(
        repository
    ).execute(reservation.identity)
    assert (
        partial.status
        is ExperimentalWorkflowPureActionSafetyStateReadStatus.LEGACY_PARTIAL
    )


def test_migrated_v3_consumed_history_is_legacy_partial(tmp_path: Path) -> None:
    _, repository, reservation, _ = _durably_commit(tmp_path)
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute("DROP TABLE reservation_lifecycle_events")
        connection.execute("DROP TABLE legacy_partial_reservations")
        connection.execute("UPDATE store_format SET version = 3")
        connection.commit()
    finally:
        connection.close()

    reopened = ExperimentalSQLitePureActionReservationRepository(
        repository.database_path
    )
    result = ExperimentalWorkflowPureActionSafetyStateReplayService(
        reopened
    ).execute(reservation.identity)
    assert (
        result.status
        is ExperimentalWorkflowPureActionSafetyStateReadStatus.LEGACY_PARTIAL
    )
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute(
            "UPDATE legacy_partial_reservations SET commit_identity = ?",
            ("0" * 64,),
        )
        connection.commit()
    finally:
        connection.close()
    corrupt = reopened.load_committed_safety_state(reservation.identity)
    assert (
        corrupt.status
        is ExperimentalWorkflowPureActionSafetyStateReadStatus.CORRUPT
    )


def test_corrupt_replay_bundle_fails_closed_without_returning_snapshot(
    tmp_path: Path,
) -> None:
    _, repository, reservation, _ = _durably_commit(tmp_path)
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute(
            "UPDATE cpn_replay_bundles SET event_bytes = ?",
            (b"{}",),
        )
        connection.commit()
    finally:
        connection.close()

    result = repository.load_committed_safety_state(reservation.identity)
    assert (
        result.status
        is ExperimentalWorkflowPureActionSafetyStateReadStatus.CORRUPT
    )
    assert result.snapshot is None
