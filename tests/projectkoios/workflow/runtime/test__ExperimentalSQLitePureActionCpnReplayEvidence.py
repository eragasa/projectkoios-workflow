"""Durable atomic linkage of compact commits and pure-CPN replay evidence."""

from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import projectkoios.workflow.persistence.pure_action_sqlite as sqlite_module
import pytest
from _pure_action_fixtures import _commit_fixture, _source
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommitService,
    ExperimentalWorkflowPureActionCpnReplayBundleFactory,
    ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec,
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus,
    ExperimentalWorkflowPureActionDurableCpnCommitService,
    ExperimentalWorkflowPureActionDurableCpnReplayService,
    ExperimentalWorkflowPureActionDurableCpnReplayStatus,
    experimental_cpn_replay_evidence,
)
from projectkoios.workflow.execution.pure_action_commit import (
    _construct_commit,
    _construct_commit_record,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservationService,
    ExperimentalWorkflowPureActionReserveStatus,
)
from projectkoios.workflow_sdk.identities import WorkflowMarkingIdentity


def _candidate(tmp_path: Path):  # type: ignore[no-untyped-def]
    fixture = _commit_fixture()
    invocation_fixture = fixture.invocation_fixture
    plan = invocation_fixture.cpn_plan
    assert plan is not None
    reservation = invocation_fixture.reservation_result.reservation
    assert reservation is not None
    firing_result = fixture.firing.firing_result
    assert firing_result is not None
    repository = ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "private" / "pure-action.sqlite3",
        predecessors=(
            ExperimentalWorkflowPureActionCurrentPredecessor(
                net_instance_identity=reservation.net_instance_identity,
                marking_identity=reservation.predecessor_marking_identity,
                revision=reservation.predecessor_revision,
            ),
        ),
    )
    assert (
        repository.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    commit = _construct_commit(
        authorized=invocation_fixture.authorized,
        reservation=reservation,
        plan=plan,
        invocation=fixture.invocation,
        firing=fixture.firing,
    )
    record = _construct_commit_record(commit, invocation_fixture.authorized)
    coordinates = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=commit.identity,
        reservation_identity=commit.reservation_identity,
        net_instance_identity=reservation.net_instance_identity,
        predecessor_marking_identity=commit.predecessor_marking_identity,
        predecessor_revision=commit.predecessor_revision,
        successor_marking_identity=commit.successor_marking_identity,
        successor_revision=commit.successor_revision,
    )
    bundle = ExperimentalWorkflowPureActionCpnReplayBundleFactory().execute(
        cpn_plan=plan,
        firing_result=firing_result,
    )
    bundle_bytes = (
        ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(bundle)
    )
    evidence = experimental_cpn_replay_evidence(record, bundle_bytes)
    return repository, reservation, coordinates, record, evidence


def _durable_orchestration(tmp_path: Path):  # type: ignore[no-untyped-def]
    fixture = _commit_fixture()
    invocation_fixture = fixture.invocation_fixture
    plan = invocation_fixture.cpn_plan
    assert plan is not None
    expected_reservation = invocation_fixture.reservation_result.reservation
    assert expected_reservation is not None
    repository = ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "orchestrated" / "pure-action.sqlite3",
        predecessors=(
            ExperimentalWorkflowPureActionCurrentPredecessor(
                net_instance_identity=expected_reservation.net_instance_identity,
                marking_identity=expected_reservation.predecessor_marking_identity,
                revision=expected_reservation.predecessor_revision,
            ),
        ),
    )
    reservation_service = ExperimentalWorkflowPureActionReservationService(
        repository,
        invocation_fixture.source_repository,
    )
    reservation_result = reservation_service.reserve(
        authorized_inputs=invocation_fixture.authorized,
        cpn_plan=plan,
    )
    assert reservation_result.reservation == expected_reservation
    return fixture, plan, repository, reservation_service, reservation_result


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


def test_commit_atomically_retains_exact_replay_evidence(
    tmp_path: Path,
) -> None:
    repository, reservation, coordinates, record, evidence = _candidate(
        tmp_path
    )

    assert (
        repository.commit_with_cpn_replay(
            reservation, coordinates, record, evidence
        )
        is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )
    reopened = ExperimentalSQLitePureActionReservationRepository(
        repository.database_path
    )
    loaded = reopened.load_cpn_replay_evidence(record.commit_identity)
    assert (
        loaded.status
        is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.FOUND
    )
    assert loaded.evidence == evidence
    assert (
        reopened.commit_with_cpn_replay(
            reservation, coordinates, record, evidence
        )
        is ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
    )


def test_concurrent_exact_replay_commits_converge(tmp_path: Path) -> None:
    repository, reservation, coordinates, record, evidence = _candidate(
        tmp_path
    )

    def commit() -> ExperimentalWorkflowPureActionCommitStatus:
        return repository.commit_with_cpn_replay(
            reservation, coordinates, record, evidence
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = tuple(executor.map(lambda _: commit(), range(2)))
    assert sorted(status.value for status in statuses) == [
        "committed",
        "idempotent",
    ]
    loaded = repository.load_cpn_replay_evidence(record.commit_identity)
    assert loaded.evidence == evidence


def test_precommit_failure_rolls_back_bundle_commit_and_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository, reservation, coordinates, record, evidence = _candidate(
        tmp_path
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
    assert (
        repository.commit_with_cpn_replay(
            reservation, coordinates, record, evidence
        )
        is ExperimentalWorkflowPureActionCommitStatus.ERROR
    )
    loaded = repository.load_cpn_replay_evidence(record.commit_identity)
    assert (
        loaded.status
        is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.ABSENT
    )
    assert repository.load_commit_record(reservation.identity) is None
    assert repository.revalidate(reservation).value == "current"


def test_durable_replay_loads_correlated_evidence_and_refires_only_cpn(
    tmp_path: Path,
) -> None:
    repository, reservation, coordinates, record, evidence = _candidate(
        tmp_path
    )
    assert (
        repository.commit_with_cpn_replay(
            reservation, coordinates, record, evidence
        )
        is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )

    replayed = ExperimentalWorkflowPureActionDurableCpnReplayService(
        repository
    ).execute(record.commit_identity)
    assert (
        replayed.status
        is ExperimentalWorkflowPureActionDurableCpnReplayStatus.REPLAYED
    )
    assert replayed.firing_result is not None
    assert (
        replayed.firing_result.identity.value
        == record.cpn_firing_result_identity
    )


def test_legacy_commit_has_closed_absent_replay_evidence(
    tmp_path: Path,
) -> None:
    repository, reservation, coordinates, record, _ = _candidate(tmp_path)
    assert (
        repository.commit(reservation, coordinates, record)
        is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )

    loaded = repository.load_cpn_replay_evidence(record.commit_identity)
    assert (
        loaded.status
        is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.ABSENT
    )
    assert loaded.evidence is None


def test_v2_store_migrates_transactionally_and_preserves_legacy_commit(
    tmp_path: Path,
) -> None:
    repository, reservation, coordinates, record, _ = _candidate(tmp_path)
    assert (
        repository.commit(reservation, coordinates, record)
        is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute("DROP TABLE commit_cpn_replay_evidence")
        connection.execute("DROP TABLE cpn_replay_bundles")
        connection.execute("UPDATE store_format SET version = 2")
        connection.commit()
    finally:
        connection.close()

    reopened = ExperimentalSQLitePureActionReservationRepository(
        repository.database_path
    )
    loaded = reopened.load_cpn_replay_evidence(record.commit_identity)
    assert (
        loaded.status
        is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.ABSENT
    )
    assert reopened.load_commit_record(reservation.identity) == record
    connection = sqlite3.connect(repository.database_path)
    try:
        assert connection.execute(
            "SELECT version FROM store_format"
        ).fetchone() == (3,)
    finally:
        connection.close()


def test_failed_v2_migration_rolls_back_schema_and_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository, _, _, record, _ = _candidate(tmp_path)
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute("DROP TABLE commit_cpn_replay_evidence")
        connection.execute("DROP TABLE cpn_replay_bundles")
        connection.execute("UPDATE store_format SET version = 2")
        connection.commit()
    finally:
        connection.close()

    def reject_schema(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise sqlite3.OperationalError("injected migration failure")

    monkeypatch.setattr(sqlite_module, "prepare_store_schema", reject_schema)
    loaded = repository.load_cpn_replay_evidence(record.commit_identity)
    assert (
        loaded.status
        is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.ERROR
    )
    connection = sqlite3.connect(repository.database_path)
    try:
        assert connection.execute(
            "SELECT version FROM store_format"
        ).fetchone() == (2,)
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert "cpn_replay_bundles" not in tables
        assert "commit_cpn_replay_evidence" not in tables
    finally:
        connection.close()


def test_corrupt_bundle_is_classified_without_returning_bytes(
    tmp_path: Path,
) -> None:
    repository, reservation, coordinates, record, evidence = _candidate(
        tmp_path
    )
    assert (
        repository.commit_with_cpn_replay(
            reservation, coordinates, record, evidence
        )
        is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )
    connection = sqlite3.connect(repository.database_path)
    try:
        connection.execute(
            "UPDATE cpn_replay_bundles SET event_bytes = ?",
            (b"{}",),
        )
        connection.commit()
    finally:
        connection.close()

    loaded = repository.load_cpn_replay_evidence(record.commit_identity)
    assert (
        loaded.status
        is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.CORRUPT
    )
    assert loaded.evidence is None
