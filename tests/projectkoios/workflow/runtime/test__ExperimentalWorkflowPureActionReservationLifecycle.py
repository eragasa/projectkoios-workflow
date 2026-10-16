"""Durable canonical reservation-lifecycle reconstruction."""

from __future__ import annotations

import json
import sqlite3
from hashlib import sha256
from pathlib import Path

import projectkoios.workflow.persistence.pure_action_sqlite as sqlite_module
import pytest
from _durable_cpn_replay_fixtures import _durable_orchestration
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionDurableCpnCommitService,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionReservationLifecycleEvent,
    ExperimentalWorkflowPureActionReservationLifecycleJsonCodec,
    ExperimentalWorkflowPureActionReservationLifecycleReadStatus,
    ExperimentalWorkflowPureActionReservationLifecycleReplayService,
    ExperimentalWorkflowPureActionReservationLifecycleState,
)


def _drop_v4_lifecycle_tables_as_v3(
    repository: ExperimentalSQLitePureActionReservationRepository,
) -> None:
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute("DROP TABLE reservation_lifecycle_events")
        connection.execute("DROP TABLE legacy_partial_reservations")
        connection.execute("UPDATE store_format SET version = 3")
        connection.commit()
    finally:
        connection.close()


def test_lifecycle_codec_is_strict_canonical_and_identity_bound(
    tmp_path: Path,
) -> None:
    _, _, _, _, reservation_result = _durable_orchestration(tmp_path)
    reservation = reservation_result.reservation
    assert reservation is not None
    event = ExperimentalWorkflowPureActionReservationLifecycleEvent(
        reservation=reservation,
        state=ExperimentalWorkflowPureActionReservationLifecycleState.RESERVED,
    )
    codec = ExperimentalWorkflowPureActionReservationLifecycleJsonCodec()
    encoded = codec.encode(event)

    assert event.identity.value == (
        "96e3d79d7302ea84ed636977d0489e45c24dcc8d31542a98da6e4f67156c5765"
    )
    assert len(encoded) == 1_180
    assert sha256(encoded).hexdigest() == (
        "ceb3ed60763d291a5ee345a5d4788d71d61b4c33c69798de6391e1b7531786fb"
    )
    assert codec.decode(encoded) == event
    document = json.loads(encoded)
    document["unknown"] = True
    malformed = json.dumps(
        document,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    try:
        codec.decode(malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown lifecycle field was accepted")


def test_new_reservation_and_commit_replay_complete_lifecycle(
    tmp_path: Path,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    reservation = reservation_result.reservation
    assert reservation is not None
    reserved = ExperimentalWorkflowPureActionReservationLifecycleReplayService(
        repository
    ).execute(reservation.identity)
    assert (
        reserved.status
        is ExperimentalWorkflowPureActionReservationLifecycleReadStatus.FOUND
    )
    assert tuple(event.state for event in reserved.events) == (
        ExperimentalWorkflowPureActionReservationLifecycleState.RESERVED,
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
    fixture.invocation_fixture.source_repository._raise_error = True
    owner_calls = fixture.invocation_fixture.firer.calls
    replayed = ExperimentalWorkflowPureActionReservationLifecycleReplayService(
        repository
    ).execute(reservation.identity)
    assert tuple(event.state for event in replayed.events) == (
        ExperimentalWorkflowPureActionReservationLifecycleState.RESERVED,
        ExperimentalWorkflowPureActionReservationLifecycleState.COMMITTED,
    )
    assert replayed.events[1].commit_identity == committed.commit.identity
    assert all(event.reservation == reservation for event in replayed.events)
    assert fixture.invocation_fixture.firer.calls == owner_calls


def test_v3_active_reservation_migrates_to_complete_lifecycle(
    tmp_path: Path,
) -> None:
    _, _, repository, _, reservation_result = _durable_orchestration(tmp_path)
    reservation = reservation_result.reservation
    assert reservation is not None
    _drop_v4_lifecycle_tables_as_v3(repository)

    reopened = ExperimentalSQLitePureActionReservationRepository(
        repository.database_path
    )
    result = reopened.load_reservation_lifecycle(reservation.identity)
    assert (
        result.status
        is ExperimentalWorkflowPureActionReservationLifecycleReadStatus.FOUND
    )
    assert result.events[0].reservation == reservation
    connection = sqlite3.connect(repository.database_path)
    try:
        assert connection.execute(
            "SELECT version FROM store_format"
        ).fetchone() == (4,)
    finally:
        connection.close()


def test_failed_v3_migration_rolls_back_lifecycle_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, _, repository, _, reservation_result = _durable_orchestration(tmp_path)
    reservation = reservation_result.reservation
    assert reservation is not None
    _drop_v4_lifecycle_tables_as_v3(repository)

    def reject_schema(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise sqlite3.OperationalError("injected migration failure")

    monkeypatch.setattr(sqlite_module, "prepare_store_schema", reject_schema)
    result = repository.load_reservation_lifecycle(reservation.identity)
    assert (
        result.status
        is ExperimentalWorkflowPureActionReservationLifecycleReadStatus.ERROR
    )
    connection = sqlite3.connect(repository.database_path)
    try:
        assert connection.execute(
            "SELECT version FROM store_format"
        ).fetchone() == (3,)
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert "reservation_lifecycle_events" not in tables
        assert "legacy_partial_reservations" not in tables
    finally:
        connection.close()


def test_v3_consumed_reservation_is_legacy_partial_not_fabricated(
    tmp_path: Path,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    reservation = reservation_result.reservation
    assert reservation is not None
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
    _drop_v4_lifecycle_tables_as_v3(repository)

    reopened = ExperimentalSQLitePureActionReservationRepository(
        repository.database_path
    )
    result = reopened.load_reservation_lifecycle(reservation.identity)
    read_status = ExperimentalWorkflowPureActionReservationLifecycleReadStatus
    assert result.status is read_status.LEGACY_PARTIAL
    assert result.events == ()


def test_lifecycle_corruption_and_absence_are_closed(tmp_path: Path) -> None:
    _, _, repository, _, reservation_result = _durable_orchestration(tmp_path)
    reservation = reservation_result.reservation
    assert reservation is not None
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute(
            "UPDATE reservation_lifecycle_events SET event_bytes = ?",
            (b"{}",),
        )
        connection.commit()
    finally:
        connection.close()

    corrupt = repository.load_reservation_lifecycle(reservation.identity)
    assert (
        corrupt.status
        is ExperimentalWorkflowPureActionReservationLifecycleReadStatus.CORRUPT
    )
    absent = repository.load_reservation_lifecycle(
        type(reservation.identity)("0" * 64)
    )
    assert (
        absent.status
        is ExperimentalWorkflowPureActionReservationLifecycleReadStatus.ABSENT
    )
