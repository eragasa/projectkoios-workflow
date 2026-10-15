"""Shared private-file and connection policy for local SQLite repositories."""

from __future__ import annotations

import os
import sqlite3
import stat
from pathlib import Path

_MAX_SQLITE_INTEGER = 2_147_483_647


class SQLiteStoreFault(Exception):
    """One closed internal SQLite store-policy or integrity fault."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def canonical_database_path(value: Path) -> Path:
    """Validate and normalize an absolute path without resolving its file."""
    if not isinstance(value, Path):
        raise TypeError("database_path must be pathlib.Path")
    if not value.is_absolute():
        raise ValueError("database_path must be absolute")
    return value.parent.resolve(strict=False) / value.name


def validate_busy_timeout(value: int) -> None:
    """Validate one SQLite busy timeout accepted by the local adapters."""
    if type(value) is not int:
        raise TypeError("busy_timeout_ms must be a built-in int")
    if not 0 <= value <= _MAX_SQLITE_INTEGER:
        raise ValueError("busy_timeout_ms is outside its bound")


def connect_private_database(
    database_path: Path,
    busy_timeout_ms: int,
) -> sqlite3.Connection:
    """Open one private no-follow SQLite file with exact durability pragmas."""
    prepare_private_database_path(database_path)
    uri = f"{database_path.as_uri()}?mode=rwc&nofollow=1"
    connection = sqlite3.connect(
        uri,
        timeout=busy_timeout_ms / 1_000,
        isolation_level=None,
        uri=True,
    )
    try:
        connection.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA synchronous = FULL")
        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()
        if mode != ("delete",):
            raise SQLiteStoreFault("unsupported_journal_mode")
    except Exception:
        connection.close()
        raise
    return connection


def prepare_private_database_path(database_path: Path) -> None:
    """Create and verify one owner-private regular database path."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if type(nofollow) is not int:
        raise SQLiteStoreFault("nofollow_unavailable")
    parent = database_path.parent
    missing: list[Path] = []
    cursor = parent
    while True:
        try:
            metadata = cursor.stat(follow_symlinks=False)
        except FileNotFoundError:
            missing.append(cursor)
            if cursor == cursor.parent:
                raise SQLiteStoreFault("database_parent_missing") from None
            cursor = cursor.parent
            continue
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise SQLiteStoreFault("unsafe_database_ancestor")
        break
    for directory in reversed(missing):
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass
        metadata = directory.stat(follow_symlinks=False)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise SQLiteStoreFault("unsafe_database_ancestor")
    for ancestor in parent.parents:
        metadata = ancestor.stat(follow_symlinks=False)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise SQLiteStoreFault("unsafe_database_ancestor")
    metadata = parent.stat(follow_symlinks=False)
    if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
        raise SQLiteStoreFault("database_parent_not_owned")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise SQLiteStoreFault("database_parent_not_private")
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | nofollow
    try:
        descriptor = os.open(database_path, flags, 0o600)
    except FileExistsError:
        descriptor = None
    if descriptor is not None:
        os.close(descriptor)
    file_metadata = database_path.stat(follow_symlinks=False)
    if stat.S_ISLNK(file_metadata.st_mode) or not stat.S_ISREG(
        file_metadata.st_mode
    ):
        raise SQLiteStoreFault("unsafe_database_file")
    if hasattr(os, "geteuid") and file_metadata.st_uid != os.geteuid():
        raise SQLiteStoreFault("database_file_not_owned")
    if file_metadata.st_nlink != 1:
        raise SQLiteStoreFault("database_file_has_links")
    if stat.S_IMODE(file_metadata.st_mode) & 0o077:
        raise SQLiteStoreFault("database_file_not_private")


def prepare_store_schema(
    connection: sqlite3.Connection,
    *,
    schema: tuple[str, ...],
    tables: tuple[str, ...],
    schema_sql_by_table: dict[str, str],
    format_identity: str,
    format_version: int,
) -> None:
    """Validate an exact schema or initialize an empty database.

    Transaction ownership remains with the adapter.
    """
    observed_tables = tuple(
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    )
    if not observed_tables:
        for statement in schema:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO store_format VALUES (?, ?)",
            (format_identity, format_version),
        )
        return
    if observed_tables != tables:
        raise SQLiteStoreFault("unrecognized_store_schema")
    definitions = dict(
        connection.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type = 'table' ORDER BY name"
        ).fetchall()
    )
    if definitions != schema_sql_by_table:
        raise SQLiteStoreFault("unrecognized_store_schema")
    metadata = connection.execute(
        "SELECT identity, version FROM store_format"
    ).fetchall()
    if metadata != [(format_identity, format_version)]:
        raise SQLiteStoreFault("unsupported_store_version")
    unexpected = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type IN ('trigger', 'view') LIMIT 1"
    ).fetchone()
    if unexpected is not None:
        raise SQLiteStoreFault("unrecognized_store_objects")


def rollback_quietly(connection: sqlite3.Connection) -> None:
    """Best-effort rollback for an adapter-owned transaction."""
    try:
        connection.execute("ROLLBACK")
    except sqlite3.Error:
        pass


__all__ = []
