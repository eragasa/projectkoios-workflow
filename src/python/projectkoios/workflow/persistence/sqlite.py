"""Private local SQLite realization of opaque revision storage."""

from __future__ import annotations

import hashlib
import os
import sqlite3
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from .store import (
    Revision,
    RevisionCommit,
    RevisionCommitResult,
    RevisionCommitStatus,
    RevisionReadRequest,
    RevisionReadResult,
    RevisionReadStatus,
    RevisionSelector,
)

_FORMAT = "projectkoios.workflow.revision-store"
_FORMAT_VERSION = 1
_SCHEMA = (
    "CREATE TABLE store_format ("
    "identity TEXT NOT NULL, version INTEGER NOT NULL)",
    "CREATE TABLE revisions ("
    "stream_identity TEXT NOT NULL, revision_identity TEXT NOT NULL, "
    "predecessor_revision_identity TEXT, schema_identity TEXT NOT NULL, "
    "content_identity TEXT NOT NULL, payload BLOB NOT NULL, "
    "idempotency_identity TEXT NOT NULL UNIQUE, envelope_digest BLOB NOT NULL, "
    "PRIMARY KEY (stream_identity, revision_identity), "
    "FOREIGN KEY (stream_identity, predecessor_revision_identity) "
    "REFERENCES revisions (stream_identity, revision_identity))",
    "CREATE TABLE heads ("
    "stream_identity TEXT PRIMARY KEY NOT NULL, "
    "revision_identity TEXT NOT NULL, "
    "FOREIGN KEY (stream_identity, revision_identity) "
    "REFERENCES revisions (stream_identity, revision_identity))",
)
_TABLES = ("heads", "revisions", "store_format")
_SCHEMA_SQL_BY_TABLE = {
    "store_format": _SCHEMA[0],
    "revisions": _SCHEMA[1],
    "heads": _SCHEMA[2],
}


class _StoreFault(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _frame(value: bytes | None) -> bytes:
    if value is None:
        return b"\x00"
    return b"\x01" + len(value).to_bytes(8, "big") + value


def _text(value: str) -> bytes:
    return value.encode("utf-8", errors="strict")


def _digest(revision: Revision, idempotency_identity: str) -> bytes:
    digest = hashlib.sha256(b"projectkoios.workflow.revision-envelope:1\x00")
    for value in (
        revision.stream_identity,
        revision.revision_identity,
        revision.predecessor_revision_identity,
        revision.schema_identity,
        revision.content_identity,
        idempotency_identity,
    ):
        digest.update(_frame(None if value is None else _text(value)))
    digest.update(_frame(revision.payload))
    return digest.digest()


def _revision_from_row(
    row: tuple[object, ...], maximum: int
) -> tuple[Revision, str]:
    if len(row) != 8:
        raise _StoreFault("invalid_revision_shape")
    (
        stream,
        revision,
        predecessor,
        schema,
        content,
        payload,
        idempotency,
        digest,
    ) = row
    text_values = (stream, revision, schema, content, idempotency)
    if any(type(value) is not str or not value for value in text_values):
        raise _StoreFault("invalid_revision_identity")
    if predecessor is not None and (
        type(predecessor) is not str or not predecessor
    ):
        raise _StoreFault("invalid_predecessor_identity")
    if type(payload) is not bytes or type(digest) is not bytes:
        raise _StoreFault("invalid_revision_payload")
    if len(payload) > maximum:
        raise _StoreFault("payload_limit")
    try:
        result = Revision(
            cast(str, stream),
            cast(str, revision),
            predecessor,
            cast(str, schema),
            cast(str, content),
            payload,
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_revision") from error
    key = cast(str, idempotency)
    if digest != _digest(result, key):
        raise _StoreFault("envelope_digest_mismatch")
    return result, key


@dataclass(frozen=True, slots=True)
class SQLiteAtomicRevisionStore:
    """Retain opaque revisions atomically in an explicit private SQLite file."""

    database_path: Path
    busy_timeout_ms: int = 5_000
    max_payload_bytes: int = 1_048_576

    def __post_init__(self) -> None:
        if not isinstance(self.database_path, Path):
            raise TypeError("database_path must be pathlib.Path")
        if not self.database_path.is_absolute():
            raise ValueError("database_path must be absolute")
        canonical_parent = self.database_path.parent.resolve(strict=False)
        object.__setattr__(
            self,
            "database_path",
            canonical_parent / self.database_path.name,
        )
        for name, value, minimum in (
            ("busy_timeout_ms", self.busy_timeout_ms, 0),
            ("max_payload_bytes", self.max_payload_bytes, 1),
        ):
            if type(value) is not int:
                raise TypeError(f"{name} must be a built-in int")
            if not minimum <= value <= 2_147_483_647:
                raise ValueError(f"{name} is outside its bound")

    def read(self, request: RevisionReadRequest) -> RevisionReadResult:
        """Read one revision without guessing through failures."""
        if type(request) is not RevisionReadRequest:
            raise TypeError("request must be RevisionReadRequest")
        connection: sqlite3.Connection | None = None
        phase = "open"
        try:
            connection = self._connect()
            phase = "prepare"
            self._prepare(connection)
            phase = "observe"
            connection.execute("BEGIN")
            if request.selector is RevisionSelector.LATEST:
                head = connection.execute(
                    "SELECT revision_identity FROM heads "
                    "WHERE stream_identity = ?",
                    (request.stream_identity,),
                ).fetchone()
                if head is None:
                    return self._read_result(request, RevisionReadStatus.ABSENT)
                if len(head) != 1 or type(head[0]) is not str:
                    raise _StoreFault("invalid_head")
                revision_identity = head[0]
            else:
                assert request.revision_identity is not None
                revision_identity = request.revision_identity
            row = connection.execute(
                "SELECT stream_identity, revision_identity, "
                "predecessor_revision_identity, schema_identity, "
                "content_identity, payload, idempotency_identity, "
                "envelope_digest FROM revisions "
                "WHERE stream_identity = ? AND revision_identity = ?",
                (request.stream_identity, revision_identity),
            ).fetchone()
            if row is None:
                return self._read_result(request, RevisionReadStatus.ABSENT)
            revision, _ = _revision_from_row(tuple(row), self.max_payload_bytes)
            return self._read_result(
                request,
                RevisionReadStatus.FOUND,
                revision=revision,
            )
        except _StoreFault as error:
            status = (
                RevisionReadStatus.INCOMPATIBLE
                if error.code
                in {
                    "unrecognized_store_objects",
                    "unrecognized_store_schema",
                    "unsupported_store_version",
                }
                else RevisionReadStatus.CORRUPT
                if error.code
                in {
                    "envelope_digest_mismatch",
                    "invalid_head",
                    "invalid_predecessor_identity",
                    "invalid_revision",
                    "invalid_revision_identity",
                    "invalid_revision_payload",
                    "payload_limit",
                }
                else RevisionReadStatus.ERROR
            )
            return self._read_result(
                request,
                status,
                diagnostics=(error.code,),
            )
        except OSError, sqlite3.Error:
            status = (
                RevisionReadStatus.INDETERMINATE
                if phase == "observe"
                else RevisionReadStatus.ERROR
            )
            return self._read_result(
                request,
                status,
                diagnostics=(f"sqlite_{phase}_failed",),
            )
        finally:
            if connection is not None:
                connection.close()

    def commit(self, commit: RevisionCommit) -> RevisionCommitResult:
        """Compare and append one revision with exact idempotency replay."""
        if type(commit) is not RevisionCommit:
            raise TypeError("commit must be RevisionCommit")
        if len(commit.candidate.payload) > self.max_payload_bytes:
            return self._commit_result(
                commit,
                RevisionCommitStatus.ERROR,
                diagnostics=("payload_limit",),
            )
        connection: sqlite3.Connection | None = None
        phase = "open"
        transaction_open = False
        try:
            connection = self._connect()
            phase = "prepare"
            self._prepare(connection)
            phase = "compare"
            connection.execute("BEGIN IMMEDIATE")
            transaction_open = True
            replay = connection.execute(
                "SELECT stream_identity, revision_identity, "
                "predecessor_revision_identity, schema_identity, "
                "content_identity, payload, idempotency_identity, "
                "envelope_digest FROM revisions "
                "WHERE idempotency_identity = ?",
                (commit.idempotency_identity,),
            ).fetchone()
            if replay is not None:
                original, original_key = _revision_from_row(
                    tuple(replay), self.max_payload_bytes
                )
                if (
                    original == commit.candidate
                    and original_key == commit.idempotency_identity
                ):
                    connection.execute("ROLLBACK")
                    transaction_open = False
                    return self._commit_result(
                        commit,
                        RevisionCommitStatus.IDEMPOTENT,
                        revision=original,
                    )
                connection.execute("ROLLBACK")
                transaction_open = False
                return self._commit_result(
                    commit,
                    RevisionCommitStatus.CONFLICT,
                    diagnostics=("idempotency_collision",),
                )
            head_row = connection.execute(
                "SELECT revision_identity FROM heads WHERE stream_identity = ?",
                (commit.candidate.stream_identity,),
            ).fetchone()
            observed_head = None if head_row is None else head_row[0]
            if observed_head is not None and type(observed_head) is not str:
                raise _StoreFault("invalid_head")
            if observed_head != commit.expected_revision_identity:
                connection.execute("ROLLBACK")
                transaction_open = False
                return self._commit_result(
                    commit,
                    RevisionCommitStatus.CONFLICT,
                    diagnostics=("compare_and_append_conflict",),
                    observed=observed_head,
                )
            existing_revision = connection.execute(
                "SELECT 1 FROM revisions WHERE stream_identity = ? "
                "AND revision_identity = ?",
                (
                    commit.candidate.stream_identity,
                    commit.candidate.revision_identity,
                ),
            ).fetchone()
            if existing_revision is not None:
                connection.execute("ROLLBACK")
                transaction_open = False
                return self._commit_result(
                    commit,
                    RevisionCommitStatus.CONFLICT,
                    diagnostics=("revision_collision",),
                    observed=observed_head,
                )
            candidate = commit.candidate
            connection.execute(
                "INSERT INTO revisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    candidate.stream_identity,
                    candidate.revision_identity,
                    candidate.predecessor_revision_identity,
                    candidate.schema_identity,
                    candidate.content_identity,
                    candidate.payload,
                    commit.idempotency_identity,
                    _digest(candidate, commit.idempotency_identity),
                ),
            )
            connection.execute(
                "INSERT INTO heads VALUES (?, ?) "
                "ON CONFLICT(stream_identity) DO UPDATE SET "
                "revision_identity = excluded.revision_identity",
                (candidate.stream_identity, candidate.revision_identity),
            )
            phase = "acknowledge"
            connection.execute("COMMIT")
            transaction_open = False
            return self._commit_result(
                commit,
                RevisionCommitStatus.COMMITTED,
                revision=candidate,
            )
        except _StoreFault as error:
            return self._commit_result(
                commit,
                RevisionCommitStatus.ERROR,
                diagnostics=(error.code,),
            )
        except OSError, sqlite3.Error:
            status = (
                RevisionCommitStatus.INDETERMINATE
                if phase == "acknowledge"
                else RevisionCommitStatus.ERROR
            )
            return self._commit_result(
                commit,
                status,
                diagnostics=(f"sqlite_{phase}_failed",),
            )
        finally:
            if connection is not None:
                if transaction_open:
                    try:
                        connection.execute("ROLLBACK")
                    except sqlite3.Error:
                        pass
                connection.close()

    def _connect(self) -> sqlite3.Connection:
        self._prepare_path()
        uri = f"{self.database_path.as_uri()}?mode=rwc&nofollow=1"
        connection = sqlite3.connect(
            uri,
            timeout=self.busy_timeout_ms / 1_000,
            isolation_level=None,
            uri=True,
        )
        connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA synchronous = FULL")
        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()
        if mode != ("delete",):
            connection.close()
            raise _StoreFault("unsupported_journal_mode")
        return connection

    def _prepare_path(self) -> None:
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if type(nofollow) is not int:
            raise _StoreFault("nofollow_unavailable")
        parent = self.database_path.parent
        missing: list[Path] = []
        cursor = parent
        while True:
            try:
                metadata = cursor.stat(follow_symlinks=False)
            except FileNotFoundError:
                missing.append(cursor)
                if cursor == cursor.parent:
                    raise _StoreFault("database_parent_missing") from None
                cursor = cursor.parent
                continue
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(
                metadata.st_mode
            ):
                raise _StoreFault("unsafe_database_ancestor")
            break
        for directory in reversed(missing):
            try:
                directory.mkdir(mode=0o700)
            except FileExistsError:
                pass
            metadata = directory.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(
                metadata.st_mode
            ):
                raise _StoreFault("unsafe_database_ancestor")
        for ancestor in parent.parents:
            metadata = ancestor.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(
                metadata.st_mode
            ):
                raise _StoreFault("unsafe_database_ancestor")
        metadata = parent.stat(follow_symlinks=False)
        if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
            raise _StoreFault("database_parent_not_owned")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise _StoreFault("database_parent_not_private")
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | nofollow
        try:
            descriptor = os.open(self.database_path, flags, 0o600)
        except FileExistsError:
            descriptor = None
        if descriptor is not None:
            os.close(descriptor)
        file_metadata = self.database_path.stat(follow_symlinks=False)
        if stat.S_ISLNK(file_metadata.st_mode) or not stat.S_ISREG(
            file_metadata.st_mode
        ):
            raise _StoreFault("unsafe_database_file")
        if hasattr(os, "geteuid") and file_metadata.st_uid != os.geteuid():
            raise _StoreFault("database_file_not_owned")
        if file_metadata.st_nlink != 1:
            raise _StoreFault("database_file_has_links")
        if stat.S_IMODE(file_metadata.st_mode) & 0o077:
            raise _StoreFault("database_file_not_private")

    @staticmethod
    def _prepare(connection: sqlite3.Connection) -> None:
        connection.execute("BEGIN IMMEDIATE")
        tables = tuple(
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' ORDER BY name"
            ).fetchall()
        )
        if not tables:
            for statement in _SCHEMA:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO store_format VALUES (?, ?)",
                (_FORMAT, _FORMAT_VERSION),
            )
        else:
            if tables != _TABLES:
                raise _StoreFault("unrecognized_store_schema")
            definitions = dict(
                connection.execute(
                    "SELECT name, sql FROM sqlite_master "
                    "WHERE type = 'table' ORDER BY name"
                ).fetchall()
            )
            if definitions != _SCHEMA_SQL_BY_TABLE:
                raise _StoreFault("unrecognized_store_schema")
            metadata = connection.execute(
                "SELECT identity, version FROM store_format"
            ).fetchall()
            if metadata != [(_FORMAT, _FORMAT_VERSION)]:
                raise _StoreFault("unsupported_store_version")
            unexpected = connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type IN ('trigger', 'view') LIMIT 1"
            ).fetchone()
            if unexpected is not None:
                raise _StoreFault("unrecognized_store_objects")
        connection.execute("COMMIT")

    @staticmethod
    def _read_result(
        request: RevisionReadRequest,
        status: RevisionReadStatus,
        *,
        revision: Revision | None = None,
        diagnostics: tuple[str, ...] = (),
    ) -> RevisionReadResult:
        return RevisionReadResult(
            status,
            request.request_identity,
            request.stream_identity,
            diagnostics,
            revision,
        )

    @staticmethod
    def _commit_result(
        commit: RevisionCommit,
        status: RevisionCommitStatus,
        *,
        revision: Revision | None = None,
        diagnostics: tuple[str, ...] = (),
        observed: str | None = None,
    ) -> RevisionCommitResult:
        return RevisionCommitResult(
            status,
            commit.candidate.stream_identity,
            commit.idempotency_identity,
            diagnostics,
            revision,
            observed,
        )
