"""SQLite retention of canonical pure-CPN replay evidence."""

from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import projectkoios.workflow.persistence.pure_action_sqlite as sqlite_module
import pytest
from _durable_cpn_replay_fixtures import _candidate
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus,
    ExperimentalWorkflowPureActionDurableCpnReplayService,
    ExperimentalWorkflowPureActionDurableCpnReplayStatus,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitStatus,
)


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
