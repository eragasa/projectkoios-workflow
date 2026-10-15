"""Verification of durable pure-action reservation and atomic commit."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

import projectkoios.workflow.persistence.pure_action_sqlite as sqlite_module
import pytest
from projectkoios.workflow.actions import (
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
)
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommittedReplayService,
    ExperimentalWorkflowPureActionCommittedReplayStatus,
)
from projectkoios.workflow.persistence import (
    ExperimentalSQLitePureActionReservationRepository,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitEventJsonCodec,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCommittedSnapshot,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionInputSourceAuthority,
    ExperimentalWorkflowPureActionInputSourceEvidenceIdentity,
    ExperimentalWorkflowPureActionInputSourceReferenceIdentity,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from projectkoios.workflow.runtime.pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)


def _digest(character: str) -> str:
    return character * 64


def _predecessor() -> ExperimentalWorkflowPureActionCurrentPredecessor:
    return ExperimentalWorkflowPureActionCurrentPredecessor(
        net_instance_identity=WorkflowNetInstanceIdentity("net:durable"),
        marking_identity=WorkflowMarkingIdentity(_digest("1")),
        revision=7,
    )


def _reservation() -> ExperimentalWorkflowPureActionReservation:
    predecessor = _predecessor()
    return ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=ExperimentalWorkflowPureActionExecutionPlanIdentity(
            _digest("2")
        ),
        execution_bindings_identity=ExperimentalWorkflowPureActionExecutionBindingsIdentity(
            _digest("3")
        ),
        selected_binding_evidence_identity=ExperimentalWorkflowSelectedBindingEvidenceIdentity(
            _digest("4")
        ),
        request_identity=WorkflowFiringRequestIdentity(_digest("5")),
        net_instance_identity=predecessor.net_instance_identity,
        predecessor_marking_identity=predecessor.marking_identity,
        predecessor_revision=predecessor.revision,
        occurrence_identity=WorkflowOccurrenceIdentity("occurrence:durable"),
        attempt_identity=WorkflowAttemptIdentity("attempt:durable"),
        attempt_ordinal=0,
        input_admission_identity=ExperimentalWorkflowPureActionAdmittedInputsIdentity(
            _digest("6")
        ),
        input_authorization_identity=ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
            _digest("7")
        ),
        cpn_plan_identity=ExperimentalWorkflowPureActionCpnPlanIdentity(
            _digest("8")
        ),
    )


def _authority() -> ExperimentalWorkflowPureActionInputSourceAuthority:
    evidence_identity = _digest("9")
    return ExperimentalWorkflowPureActionInputSourceAuthority(
        reference_identity=ExperimentalWorkflowPureActionInputSourceReferenceIdentity(
            _digest("a")
        ),
        revision_identity=ExperimentalWorkflowPureActionInputSourceRevisionIdentity(
            evidence_identity
        ),
        evidence_identity=ExperimentalWorkflowPureActionInputSourceEvidenceIdentity(
            evidence_identity
        ),
    )


def _commit_state(
    *,
    commit_character: str = "b",
    successor_character: str = "c",
) -> tuple[
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitRecord,
]:
    reservation = _reservation()
    commit_identity = ExperimentalWorkflowPureActionCommitIdentity(
        _digest(commit_character)
    )
    successor = WorkflowMarkingIdentity(_digest(successor_character))
    coordinates = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=commit_identity,
        reservation_identity=reservation.identity,
        net_instance_identity=reservation.net_instance_identity,
        predecessor_marking_identity=reservation.predecessor_marking_identity,
        predecessor_revision=reservation.predecessor_revision,
        successor_marking_identity=successor,
        successor_revision=reservation.predecessor_revision + 1,
    )
    assert reservation.cpn_plan_identity is not None
    assert reservation.input_authorization_identity is not None
    record = ExperimentalWorkflowPureActionCommitRecord(
        commit_identity=commit_identity,
        cpn_plan_identity=reservation.cpn_plan_identity,
        reservation_identity=reservation.identity,
        net_instance_identity=reservation.net_instance_identity,
        input_authorization_identity=reservation.input_authorization_identity,
        source_authorities=(_authority(),),
        invocation_outcome_identity=_digest("d"),
        request_identity=reservation.request_identity,
        owner_result_identity=WorkflowFiringResultIdentity(_digest("e")),
        mapped_result_identity=_digest("f"),
        firing_outcome_identity=_digest("0"),
        cpn_firing_result_identity=_digest("1"),
        predecessor_marking_identity=reservation.predecessor_marking_identity,
        predecessor_revision=reservation.predecessor_revision,
        successor_marking_identity=successor,
        successor_revision=reservation.predecessor_revision + 1,
    )
    return coordinates, record


def _repository(
    tmp_path: Path,
    *,
    bootstrap: bool = True,
    name: str = "pure-action.sqlite3",
) -> ExperimentalSQLitePureActionReservationRepository:
    predecessors = (_predecessor(),) if bootstrap else ()
    return ExperimentalSQLitePureActionReservationRepository(
        tmp_path / "private" / name,
        predecessors=predecessors,
        busy_timeout_ms=10_000,
    )


def test_durable_commit_reopens_complete_record_and_current_state(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    coordinates, record = _commit_state()

    assert (
        repository.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    assert (
        repository.commit(reservation, coordinates, record)
        is ExperimentalWorkflowPureActionCommitStatus.COMMITTED
    )

    reopened = _repository(tmp_path, bootstrap=False)
    assert reopened.load_commit(reservation.identity) == coordinates
    assert reopened.load_commit_record(reservation.identity) == record
    assert reopened.load_commit_event(reservation.identity) == (
        ExperimentalWorkflowPureActionCommitEventJsonCodec().encode(record)
    )
    assert reopened.current_predecessor(reservation.net_instance_identity) == (
        ExperimentalWorkflowPureActionCurrentPredecessor(
            net_instance_identity=reservation.net_instance_identity,
            marking_identity=coordinates.successor_marking_identity,
            revision=coordinates.successor_revision,
        )
    )
    assert (
        reopened.revalidate(reservation)
        is ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
    )
    assert (
        reopened.commit(reservation, coordinates, record)
        is ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
    )
    assert repository.database_path.parent.stat().st_mode & 0o777 == 0o700
    assert repository.database_path.stat().st_mode & 0o777 == 0o600
    assert not Path(f"{repository.database_path}-wal").exists()
    assert not Path(f"{repository.database_path}-shm").exists()


def test_commit_event_codec_is_strict_canonical_and_identity_only() -> None:
    _, record = _commit_state()
    codec = ExperimentalWorkflowPureActionCommitEventJsonCodec()

    encoded = codec.encode(record)

    assert codec.encode(record) == encoded
    assert codec.decode(encoded) == record
    assert b"payload" not in encoded
    assert b"locator" not in encoded
    with pytest.raises(ValueError, match="canonical JSON"):
        codec.decode(b" " + encoded)
    parsed = json.loads(encoded)
    assert (
        parsed["commit"]["net_instance_identity"]
        == record.net_instance_identity.value
    )
    parsed["unexpected"] = True
    unknown = json.dumps(
        parsed,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    with pytest.raises(ValueError, match="closed schema"):
        codec.decode(unknown)


def test_committed_snapshot_rejects_cross_net_coordinates() -> None:
    coordinates, record = _commit_state()
    changed = replace(
        record,
        net_instance_identity=WorkflowNetInstanceIdentity("net:other"),
    )

    with pytest.raises(ValueError, match="coordinates differ"):
        ExperimentalWorkflowPureActionCommittedSnapshot(
            coordinates=coordinates,
            record=changed,
            event_bytes=(
                ExperimentalWorkflowPureActionCommitEventJsonCodec().encode(
                    changed
                )
            ),
        )


def test_commit_event_codec_rejects_changed_source_authority_identity() -> None:
    _, record = _commit_state()
    codec = ExperimentalWorkflowPureActionCommitEventJsonCodec()
    parsed = json.loads(codec.encode(record))
    parsed["commit"]["source_authorities"][0]["authority_identity"] = _digest(
        "f"
    )
    changed = json.dumps(
        parsed,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()

    with pytest.raises(ValueError, match="differs from its fields"):
        codec.decode(changed)


def test_precommit_failure_rolls_back_every_durable_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    coordinates, record = _commit_state()
    assert (
        repository.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )

    def fail_before_commit(
        operation: str,
        connection: sqlite3.Connection,
    ) -> None:
        del connection
        if operation == "commit":
            raise RuntimeError("injected precommit failure")

    monkeypatch.setattr(
        sqlite_module,
        "_before_transaction_commit",
        fail_before_commit,
    )
    assert (
        repository.commit(reservation, coordinates, record)
        is ExperimentalWorkflowPureActionCommitStatus.ERROR
    )

    reopened = _repository(tmp_path, bootstrap=False)
    assert reopened.load_commit(reservation.identity) is None
    assert reopened.load_commit_record(reservation.identity) is None
    assert reopened.current_predecessor(reservation.net_instance_identity) == (
        _predecessor()
    )
    assert (
        reopened.revalidate(reservation)
        is ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_process_crash_discards_uncommitted_marking_change(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    assert (
        repository.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    script = """
import os
import sqlite3
import sys
connection = sqlite3.connect(sys.argv[1], isolation_level=None)
connection.execute("BEGIN IMMEDIATE")
connection.execute(
    "UPDATE current_predecessors SET marking_identity = ?, revision = ?",
    ("f" * 64, 999),
)
os._exit(0)
"""
    subprocess.run(
        [sys.executable, "-c", script, os.fspath(repository.database_path)],
        check=True,
    )

    reopened = _repository(tmp_path, bootstrap=False)
    assert reopened.current_predecessor(reservation.net_instance_identity) == (
        _predecessor()
    )
    assert (
        reopened.revalidate(reservation)
        is ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
    )


def test_concurrent_exact_commits_have_one_commit_and_one_idempotent_replay(
    tmp_path: Path,
) -> None:
    first = _repository(tmp_path)
    second = _repository(tmp_path, bootstrap=False)
    reservation = _reservation()
    coordinates, record = _commit_state()
    assert (
        first.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    barrier = Barrier(2)

    def commit(
        repository_index: int,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        barrier.wait()
        selected = first if repository_index == 0 else second
        return selected.commit(reservation, coordinates, record)

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = tuple(executor.map(commit, range(2)))

    assert sorted(statuses) == sorted(
        (
            ExperimentalWorkflowPureActionCommitStatus.COMMITTED,
            ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT,
        )
    )


def test_concurrent_distinct_commits_have_one_winner(
    tmp_path: Path,
) -> None:
    first = _repository(tmp_path)
    second = _repository(tmp_path, bootstrap=False)
    reservation = _reservation()
    candidates = (
        _commit_state(commit_character="b", successor_character="c"),
        _commit_state(commit_character="c", successor_character="d"),
    )
    assert (
        first.reserve(reservation)
        is ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    barrier = Barrier(2)

    def commit(
        repository_index: int,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        barrier.wait()
        selected = first if repository_index == 0 else second
        coordinates, record = candidates[repository_index]
        return selected.commit(reservation, coordinates, record)

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = tuple(executor.map(commit, range(2)))

    assert sorted(statuses) == sorted(
        (
            ExperimentalWorkflowPureActionCommitStatus.COMMITTED,
            ExperimentalWorkflowPureActionCommitStatus.CONFLICT,
        )
    )
    retained = first.load_commit(reservation.identity)
    assert retained in tuple(item[0] for item in candidates)


def test_commit_record_corruption_fails_closed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    coordinates, record = _commit_state()
    repository.reserve(reservation)
    repository.commit(reservation, coordinates, record)
    with sqlite3.connect(repository.database_path) as connection:
        connection.execute(
            "UPDATE commits SET mapped_result_identity = ?",
            (_digest("2"),),
        )

    replayed = ExperimentalWorkflowPureActionCommittedReplayService(
        repository
    ).execute(reservation.identity)
    assert (
        replayed.status
        is ExperimentalWorkflowPureActionCommittedReplayStatus.CORRUPT
    )
    assert replayed.diagnostics == ("commit_event_record_mismatch",)
    with pytest.raises(RuntimeError, match="commit_event_record_mismatch"):
        repository.load_commit_record(reservation.identity)


def test_incompatible_store_version_has_closed_replay_outcome(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    repository.current_predecessor(reservation.net_instance_identity)
    with sqlite3.connect(repository.database_path) as connection:
        connection.execute("UPDATE store_format SET version = 999")

    replayed = ExperimentalWorkflowPureActionCommittedReplayService(
        repository
    ).execute(reservation.identity)

    assert (
        replayed.status
        is ExperimentalWorkflowPureActionCommittedReplayStatus.INCOMPATIBLE
    )
    assert replayed.diagnostics == ("unsupported_store_version",)


def test_current_predecessor_corruption_fails_closed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    repository.current_predecessor(_predecessor().net_instance_identity)
    with sqlite3.connect(repository.database_path) as connection:
        connection.execute(
            "UPDATE current_predecessors SET revision = ?",
            (999,),
        )

    with pytest.raises(RuntimeError, match="predecessor_digest_mismatch"):
        repository.current_predecessor(_predecessor().net_instance_identity)


def test_store_retains_only_compact_identities_and_evidence_references(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    coordinates, record = _commit_state()
    repository.reserve(reservation)
    repository.commit(reservation, coordinates, record)

    with sqlite3.connect(repository.database_path) as connection:
        commit_columns = tuple(
            row[1] for row in connection.execute("PRAGMA table_info(commits)")
        )
        authority_row = connection.execute(
            "SELECT authority_identity, reference_identity, revision_identity, "
            "evidence_identity FROM commit_source_authorities"
        ).fetchone()

    assert all(
        "payload" not in column and "locator" not in column
        for column in commit_columns
    )
    authority = record.source_authorities[0]
    assert authority_row == (
        authority.identity.value,
        authority.reference_identity.value,
        authority.revision_identity.value,
        authority.evidence_identity.value,
    )


def test_durable_repository_rejects_symlink_database(tmp_path: Path) -> None:
    directory = tmp_path / "private"
    directory.mkdir(mode=0o700)
    target = directory / "target.sqlite3"
    target.touch()
    path = directory / "pure-action.sqlite3"
    path.symlink_to(target)
    repository = ExperimentalSQLitePureActionReservationRepository(path)

    with pytest.raises(RuntimeError, match="unsafe_database_file"):
        repository.current_predecessor(_predecessor().net_instance_identity)


def test_durable_repository_requires_complete_commit_record(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    reservation = _reservation()
    coordinates, _ = _commit_state()
    repository.reserve(reservation)

    with pytest.raises(ValueError, match="complete commit record"):
        repository.commit(reservation, coordinates)


def test_changed_bootstrap_predecessor_fails_closed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    repository.current_predecessor(_predecessor().net_instance_identity)
    changed = replace(
        _predecessor(),
        marking_identity=WorkflowMarkingIdentity(_digest("f")),
    )
    conflicting = ExperimentalSQLitePureActionReservationRepository(
        repository.database_path,
        predecessors=(changed,),
    )

    with pytest.raises(RuntimeError, match="predecessor_bootstrap_conflict"):
        conflicting.current_predecessor(changed.net_instance_identity)
