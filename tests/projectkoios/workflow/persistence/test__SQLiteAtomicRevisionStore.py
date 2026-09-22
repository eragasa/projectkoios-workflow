"""Software verification for private atomic SQLite revision storage."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from projectkoios.workflow.persistence import (
    Revision,
    RevisionCommit,
    RevisionCommitStatus,
    RevisionReadRequest,
    RevisionReadStatus,
    RevisionSelector,
    SQLiteAtomicRevisionStore,
)


def revision(
    identity: str,
    predecessor: str | None,
    payload: bytes,
) -> Revision:
    return Revision(
        "run:test",
        identity,
        predecessor,
        "fixture:1",
        hashlib.sha256(payload).hexdigest(),
        payload,
    )


def store(tmp_path: Path) -> SQLiteAtomicRevisionStore:
    return SQLiteAtomicRevisionStore(tmp_path / "private" / "workflow.sqlite3")


def test__sqlite_store__commits_replays_and_reopens_history(
    tmp_path: Path,
) -> None:
    first = revision("revision:1", None, b"first")
    second = revision("revision:2", first.revision_identity, b"second")
    selected = store(tmp_path)

    first_result = selected.commit(RevisionCommit(None, first, "commit:1"))
    second_result = selected.commit(
        RevisionCommit(first.revision_identity, second, "commit:2")
    )
    replay = selected.commit(RevisionCommit(None, first, "commit:1"))
    reopened = store(tmp_path).read(
        RevisionReadRequest(
            "read:latest",
            first.stream_identity,
            RevisionSelector.LATEST,
        )
    )
    historical = store(tmp_path).read(
        RevisionReadRequest(
            "read:first",
            first.stream_identity,
            RevisionSelector.EXPLICIT,
            first.revision_identity,
        )
    )

    assert first_result.status is RevisionCommitStatus.COMMITTED
    assert second_result.status is RevisionCommitStatus.COMMITTED
    assert replay.status is RevisionCommitStatus.IDEMPOTENT
    assert replay.revision == first
    assert reopened.status is RevisionReadStatus.FOUND
    assert reopened.revision == second
    assert historical.status is RevisionReadStatus.FOUND
    assert historical.revision == first
    assert (tmp_path / "private").stat().st_mode & 0o777 == 0o700
    assert (
        tmp_path / "private" / "workflow.sqlite3"
    ).stat().st_mode & 0o777 == 0o600


def test__sqlite_store__rejects_stale_and_changed_idempotency(
    tmp_path: Path,
) -> None:
    first = revision("revision:1", None, b"first")
    selected = store(tmp_path)
    assert (
        selected.commit(RevisionCommit(None, first, "commit:1")).status
        is RevisionCommitStatus.COMMITTED
    )
    stale = revision("revision:2", None, b"stale")
    changed = revision("revision:changed", None, b"changed")

    stale_result = selected.commit(RevisionCommit(None, stale, "commit:2"))
    collision = selected.commit(RevisionCommit(None, changed, "commit:1"))

    assert stale_result.status is RevisionCommitStatus.CONFLICT
    assert stale_result.diagnostics == ("compare_and_append_conflict",)
    assert stale_result.observed_revision_identity == first.revision_identity
    assert collision.status is RevisionCommitStatus.CONFLICT
    assert collision.diagnostics == ("idempotency_collision",)


def test__sqlite_store__serializes_concurrent_compare_and_append(
    tmp_path: Path,
) -> None:
    path = tmp_path / "private" / "workflow.sqlite3"
    first = SQLiteAtomicRevisionStore(path, busy_timeout_ms=10_000)
    second = SQLiteAtomicRevisionStore(path, busy_timeout_ms=10_000)
    candidates = (
        revision("revision:a", None, b"a"),
        revision("revision:b", None, b"b"),
    )
    barrier = Barrier(2)

    def commit(index: int) -> RevisionCommitStatus:
        barrier.wait()
        selected = first if index == 0 else second
        return selected.commit(
            RevisionCommit(None, candidates[index], f"commit:{index}")
        ).status

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = tuple(executor.map(commit, range(2)))

    assert sorted(statuses) == sorted(
        (RevisionCommitStatus.COMMITTED, RevisionCommitStatus.CONFLICT)
    )
    loaded = first.read(
        RevisionReadRequest("read:winner", "run:test", RevisionSelector.LATEST)
    )
    assert loaded.status is RevisionReadStatus.FOUND
    assert loaded.revision in candidates


def test__sqlite_store__reports_tampered_payload_as_corrupt(
    tmp_path: Path,
) -> None:
    selected = store(tmp_path)
    first = revision("revision:1", None, b"first")
    selected.commit(RevisionCommit(None, first, "commit:1"))
    with sqlite3.connect(selected.database_path) as connection:
        connection.execute(
            "UPDATE revisions SET payload = ? WHERE revision_identity = ?",
            (b"tampered", first.revision_identity),
        )

    result = selected.read(
        RevisionReadRequest(
            "read:tampered",
            first.stream_identity,
            RevisionSelector.LATEST,
        )
    )

    assert result.status is RevisionReadStatus.CORRUPT
    assert result.revision is None
    assert result.diagnostics == ("envelope_digest_mismatch",)


def test__sqlite_store__reports_changed_schema_as_incompatible(
    tmp_path: Path,
) -> None:
    selected = store(tmp_path)
    selected.read(
        RevisionReadRequest("read:create", "run:test", RevisionSelector.LATEST)
    )
    with sqlite3.connect(selected.database_path) as connection:
        connection.execute("ALTER TABLE heads ADD COLUMN unexpected TEXT")

    result = selected.read(
        RevisionReadRequest(
            "read:incompatible", "run:test", RevisionSelector.LATEST
        )
    )

    assert result.status is RevisionReadStatus.INCOMPATIBLE
    assert result.revision is None
    assert result.diagnostics == ("unrecognized_store_schema",)


def test__sqlite_store__fails_closed_for_symlink_database(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "private"
    directory.mkdir(mode=0o700)
    target = directory / "target.sqlite3"
    target.touch()
    path = directory / "workflow.sqlite3"
    path.symlink_to(target)
    selected = SQLiteAtomicRevisionStore(path)

    result = selected.read(
        RevisionReadRequest(
            "read:unsafe",
            "run:test",
            RevisionSelector.LATEST,
        )
    )

    assert result.status is RevisionReadStatus.ERROR
    assert result.revision is None
    assert result.diagnostics == ("unsafe_database_file",)


def test__sqlite_store__does_not_repair_insecure_parent_permissions(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "shared"
    directory.mkdir(mode=0o755)
    directory.chmod(0o755)
    selected = SQLiteAtomicRevisionStore(directory / "workflow.sqlite3")

    result = selected.read(
        RevisionReadRequest(
            "read:private-boundary", "run:test", RevisionSelector.LATEST
        )
    )

    assert result.status is RevisionReadStatus.ERROR
    assert result.diagnostics == ("database_parent_not_private",)
    assert directory.stat().st_mode & 0o777 == 0o755


def test__sqlite_store__rejects_invalid_configuration(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="absolute"):
        SQLiteAtomicRevisionStore(Path("relative.sqlite3"))
    with pytest.raises(TypeError, match="built-in int"):
        SQLiteAtomicRevisionStore(
            tmp_path / "store.sqlite3", busy_timeout_ms=True
        )
    with pytest.raises(ValueError, match="outside"):
        SQLiteAtomicRevisionStore(
            tmp_path / "store.sqlite3", max_payload_bytes=0
        )


def test__sqlite_store__leaves_no_wal_sidecars(tmp_path: Path) -> None:
    selected = store(tmp_path)
    first = revision("revision:1", None, b"first")
    selected.commit(RevisionCommit(None, first, "commit:1"))

    assert not Path(f"{selected.database_path}-wal").exists()
    assert not Path(f"{selected.database_path}-shm").exists()
    assert os.path.isfile(selected.database_path)
