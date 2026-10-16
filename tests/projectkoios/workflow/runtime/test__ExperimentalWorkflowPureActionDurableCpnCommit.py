"""Authoritative orchestration of durable CPN replay commits."""

import sqlite3
from pathlib import Path

import projectkoios.workflow.persistence.pure_action_sqlite as sqlite_module
import pytest
from _durable_cpn_replay_fixtures import _durable_orchestration
from _pure_action_fixtures import _source
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommitService,
    ExperimentalWorkflowPureActionDurableCpnCommitService,
    ExperimentalWorkflowPureActionDurableCpnReplayService,
    ExperimentalWorkflowPureActionDurableCpnReplayStatus,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionReservationLifecycleReadStatus,
    ExperimentalWorkflowPureActionReservationLifecycleState,
)
from projectkoios.workflow_sdk.identities import WorkflowMarkingIdentity


def test_authoritative_commit_constructs_and_persists_replay_internally(
    tmp_path: Path,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    owner_calls = fixture.invocation_fixture.firer.calls

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
    repeated = ExperimentalWorkflowPureActionDurableCpnCommitService(
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
        repeated.status is ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
    )
    replayed = ExperimentalWorkflowPureActionDurableCpnReplayService(
        repository
    ).execute(committed.commit.identity)
    assert (
        replayed.status
        is ExperimentalWorkflowPureActionDurableCpnReplayStatus.REPLAYED
    )
    assert fixture.invocation_fixture.firer.calls == owner_calls == 1


def test_authoritative_commit_rolls_back_every_row_on_precommit_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )

    def fail_before_commit(
        operation: str, connection: sqlite3.Connection
    ) -> None:
        del operation, connection
        raise RuntimeError("injected")

    monkeypatch.setattr(
        sqlite_module,
        "_before_transaction_commit",
        fail_before_commit,
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
    assert committed.status is ExperimentalWorkflowPureActionCommitStatus.ERROR
    reservation = reservation_result.reservation
    assert reservation is not None
    assert repository.load_commit(reservation.identity) is None
    assert repository.revalidate(reservation).value == "current"
    lifecycle = repository.load_reservation_lifecycle(reservation.identity)
    assert (
        lifecycle.status
        is ExperimentalWorkflowPureActionReservationLifecycleReadStatus.FOUND
    )
    assert tuple(event.state for event in lifecycle.events) == (
        ExperimentalWorkflowPureActionReservationLifecycleState.RESERVED,
    )
    connection = sqlite3.connect(repository.database_path)
    try:
        assert connection.execute(
            "SELECT count(*) FROM commits"
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM cpn_replay_bundles"
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM commit_cpn_replay_evidence"
        ).fetchone() == (0,)
    finally:
        connection.close()


def test_authoritative_commit_rejects_stale_predecessor(tmp_path: Path) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    reservation = reservation_result.reservation
    assert reservation is not None
    changed_marking = WorkflowMarkingIdentity("f" * 64)
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute(
            "UPDATE current_predecessors SET marking_identity = ?, "
            "revision = ?, coordinate_digest = ? "
            "WHERE net_instance_identity = ?",
            (
                changed_marking.value,
                reservation.predecessor_revision + 1,
                sqlite_module._predecessor_digest(
                    reservation.net_instance_identity,
                    changed_marking,
                    reservation.predecessor_revision + 1,
                ),
                reservation.net_instance_identity.value,
            ),
        )
        connection.commit()
    finally:
        connection.close()

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
    assert committed.status is ExperimentalWorkflowPureActionCommitStatus.STALE
    assert repository.load_commit(reservation.identity) is None


def test_authoritative_commit_rejects_repository_mismatch(
    tmp_path: Path,
) -> None:
    _, _, repository, reservation_service, _ = _durable_orchestration(tmp_path)
    other = ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "other" / "pure-action.sqlite3"
    )
    with pytest.raises(ValueError, match="same repository"):
        ExperimentalWorkflowPureActionDurableCpnCommitService(
            reservation_service,
            other,
        )
    assert repository is not other


def test_authoritative_commit_revalidates_sources_before_atomic_boundary(
    tmp_path: Path,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
    )
    fixture.invocation_fixture.source_repository.replace(
        _source(payload=b'{"changed":true}')
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

    assert committed.status is ExperimentalWorkflowPureActionCommitStatus.STALE
    reservation = reservation_result.reservation
    assert reservation is not None
    assert repository.load_commit(reservation.identity) is None
    assert repository.revalidate(reservation).value == "current"


def test_authoritative_replay_commit_conflicts_with_legacy_compact_commit(
    tmp_path: Path,
) -> None:
    fixture, plan, repository, reservation_service, reservation_result = (
        _durable_orchestration(tmp_path)
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

    replayable = ExperimentalWorkflowPureActionDurableCpnCommitService(
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
        replayable.status is ExperimentalWorkflowPureActionCommitStatus.CONFLICT
    )
    assert replayable.diagnostics == ("cpn_replay_evidence_conflict",)
