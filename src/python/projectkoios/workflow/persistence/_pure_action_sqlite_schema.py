"""Exact schema and transactional migrations for pure-action SQLite."""

from __future__ import annotations

import sqlite3

from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionReservationLifecycleEvent,
    ExperimentalWorkflowPureActionReservationLifecycleState,
)

from ._pure_action_reservation_lifecycle_sqlite_rows import (
    _insert_lifecycle_event,
)
from ._pure_action_sqlite_rows import _reservation_from_row

_FORMAT = "projectkoios.workflow.experimental-pure-action-store"
_FORMAT_VERSION = 4
_SCHEMA = (
    "CREATE TABLE store_format ("
    "identity TEXT NOT NULL, version INTEGER NOT NULL)",
    "CREATE TABLE initial_predecessors ("
    "net_instance_identity TEXT PRIMARY KEY NOT NULL, "
    "marking_identity TEXT NOT NULL, revision INTEGER NOT NULL, "
    "coordinate_digest BLOB NOT NULL)",
    "CREATE TABLE current_predecessors ("
    "net_instance_identity TEXT PRIMARY KEY NOT NULL, "
    "marking_identity TEXT NOT NULL, revision INTEGER NOT NULL, "
    "coordinate_digest BLOB NOT NULL)",
    "CREATE TABLE active_reservations ("
    "reservation_identity TEXT PRIMARY KEY NOT NULL, "
    "execution_plan_identity TEXT NOT NULL, "
    "execution_bindings_identity TEXT NOT NULL, "
    "selected_binding_evidence_identity TEXT NOT NULL, "
    "request_identity TEXT NOT NULL, "
    "net_instance_identity TEXT UNIQUE NOT NULL, "
    "predecessor_marking_identity TEXT NOT NULL, "
    "predecessor_revision INTEGER NOT NULL, "
    "occurrence_identity TEXT NOT NULL, attempt_identity TEXT NOT NULL, "
    "attempt_ordinal INTEGER NOT NULL, input_admission_identity TEXT, "
    "input_authorization_identity TEXT, cpn_plan_identity TEXT)",
    "CREATE TABLE consumed_reservations ("
    "reservation_identity TEXT PRIMARY KEY NOT NULL)",
    "CREATE TABLE commits ("
    "reservation_identity TEXT PRIMARY KEY NOT NULL, "
    "commit_identity TEXT UNIQUE NOT NULL, "
    "net_instance_identity TEXT NOT NULL, cpn_plan_identity TEXT NOT NULL, "
    "input_authorization_identity TEXT NOT NULL, "
    "invocation_outcome_identity TEXT NOT NULL, "
    "request_identity TEXT NOT NULL, owner_result_identity TEXT NOT NULL, "
    "mapped_result_identity TEXT NOT NULL, "
    "firing_outcome_identity TEXT NOT NULL, "
    "cpn_firing_result_identity TEXT NOT NULL, "
    "predecessor_marking_identity TEXT NOT NULL, "
    "predecessor_revision INTEGER NOT NULL, "
    "successor_marking_identity TEXT NOT NULL, "
    "successor_revision INTEGER NOT NULL, event_bytes BLOB NOT NULL, "
    "record_digest BLOB NOT NULL)",
    "CREATE TABLE commit_source_authorities ("
    "commit_identity TEXT NOT NULL, ordinal INTEGER NOT NULL, "
    "authority_identity TEXT NOT NULL, reference_identity TEXT NOT NULL, "
    "revision_identity TEXT NOT NULL, evidence_identity TEXT NOT NULL, "
    "PRIMARY KEY (commit_identity, ordinal), "
    "FOREIGN KEY (commit_identity) REFERENCES commits (commit_identity))",
    "CREATE TABLE cpn_replay_bundles ("
    "bundle_identity TEXT PRIMARY KEY NOT NULL, event_bytes BLOB NOT NULL, "
    "event_digest BLOB NOT NULL)",
    "CREATE TABLE commit_cpn_replay_evidence ("
    "commit_identity TEXT PRIMARY KEY NOT NULL, "
    "evidence_identity TEXT UNIQUE NOT NULL, bundle_identity TEXT NOT NULL, "
    "cpn_plan_identity TEXT NOT NULL, "
    "cpn_firing_result_identity TEXT NOT NULL, "
    "predecessor_marking_identity TEXT NOT NULL, "
    "successor_marking_identity TEXT NOT NULL, evidence_digest BLOB NOT NULL, "
    "FOREIGN KEY (commit_identity) REFERENCES commits (commit_identity), "
    "FOREIGN KEY (bundle_identity) REFERENCES cpn_replay_bundles "
    "(bundle_identity))",
    "CREATE TABLE reservation_lifecycle_events ("
    "reservation_identity TEXT NOT NULL, ordinal INTEGER NOT NULL, "
    "lifecycle_identity TEXT UNIQUE NOT NULL, state TEXT NOT NULL, "
    "commit_identity TEXT, event_bytes BLOB NOT NULL, "
    "event_digest BLOB NOT NULL, "
    "PRIMARY KEY (reservation_identity, ordinal), "
    "FOREIGN KEY (commit_identity) REFERENCES commits (commit_identity))",
    "CREATE TABLE legacy_partial_reservations ("
    "reservation_identity TEXT PRIMARY KEY NOT NULL, commit_identity TEXT)",
)
_SCHEMA_V2 = _SCHEMA[:7]
_TABLES_V2 = (
    "active_reservations",
    "commit_source_authorities",
    "commits",
    "consumed_reservations",
    "current_predecessors",
    "initial_predecessors",
    "store_format",
)
_SCHEMA_V2_SQL_BY_TABLE = {
    "store_format": _SCHEMA_V2[0],
    "initial_predecessors": _SCHEMA_V2[1],
    "current_predecessors": _SCHEMA_V2[2],
    "active_reservations": _SCHEMA_V2[3],
    "consumed_reservations": _SCHEMA_V2[4],
    "commits": _SCHEMA_V2[5],
    "commit_source_authorities": _SCHEMA_V2[6],
}
_SCHEMA_V3 = _SCHEMA[:9]
_TABLES_V3 = (
    "active_reservations",
    "commit_cpn_replay_evidence",
    "commit_source_authorities",
    "commits",
    "consumed_reservations",
    "cpn_replay_bundles",
    "current_predecessors",
    "initial_predecessors",
    "store_format",
)
_SCHEMA_V3_SQL_BY_TABLE = {
    "store_format": _SCHEMA_V3[0],
    "initial_predecessors": _SCHEMA_V3[1],
    "current_predecessors": _SCHEMA_V3[2],
    "active_reservations": _SCHEMA_V3[3],
    "consumed_reservations": _SCHEMA_V3[4],
    "commits": _SCHEMA_V3[5],
    "commit_source_authorities": _SCHEMA_V3[6],
    "cpn_replay_bundles": _SCHEMA_V3[7],
    "commit_cpn_replay_evidence": _SCHEMA_V3[8],
}
_TABLES = (
    "active_reservations",
    "commit_cpn_replay_evidence",
    "commit_source_authorities",
    "commits",
    "consumed_reservations",
    "cpn_replay_bundles",
    "current_predecessors",
    "initial_predecessors",
    "legacy_partial_reservations",
    "reservation_lifecycle_events",
    "store_format",
)
_SCHEMA_SQL_BY_TABLE = {
    "store_format": _SCHEMA[0],
    "initial_predecessors": _SCHEMA[1],
    "current_predecessors": _SCHEMA[2],
    "active_reservations": _SCHEMA[3],
    "consumed_reservations": _SCHEMA[4],
    "commits": _SCHEMA[5],
    "commit_source_authorities": _SCHEMA[6],
    "cpn_replay_bundles": _SCHEMA[7],
    "commit_cpn_replay_evidence": _SCHEMA[8],
    "reservation_lifecycle_events": _SCHEMA[9],
    "legacy_partial_reservations": _SCHEMA[10],
}


def _migrate_v2_store(connection: sqlite3.Connection) -> None:
    tables = tuple(
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    )
    if tables != _TABLES_V2:
        return
    definitions = dict(
        connection.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type = 'table' ORDER BY name"
        ).fetchall()
    )
    metadata = connection.execute(
        "SELECT identity, version FROM store_format"
    ).fetchall()
    unexpected = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type IN ('trigger', 'view') LIMIT 1"
    ).fetchone()
    if (
        definitions != _SCHEMA_V2_SQL_BY_TABLE
        or metadata != [(_FORMAT, 2)]
        or unexpected is not None
    ):
        return
    for statement in _SCHEMA_V3[7:]:
        connection.execute(statement)
    connection.execute("UPDATE store_format SET version = 3")


def _migrate_v3_store(connection: sqlite3.Connection) -> None:
    tables = tuple(
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    )
    if tables != _TABLES_V3:
        return
    definitions = dict(
        connection.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type = 'table' ORDER BY name"
        ).fetchall()
    )
    metadata = connection.execute(
        "SELECT identity, version FROM store_format"
    ).fetchall()
    unexpected = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type IN ('trigger', 'view') LIMIT 1"
    ).fetchone()
    if (
        definitions != _SCHEMA_V3_SQL_BY_TABLE
        or metadata != [(_FORMAT, 3)]
        or unexpected is not None
    ):
        return
    for statement in _SCHEMA[9:]:
        connection.execute(statement)
    for row in connection.execute(
        "SELECT * FROM active_reservations"
    ).fetchall():
        reservation = _reservation_from_row(tuple(row))
        _insert_lifecycle_event(
            connection,
            ExperimentalWorkflowPureActionReservationLifecycleEvent(
                reservation=reservation,
                state=ExperimentalWorkflowPureActionReservationLifecycleState.RESERVED,
            ),
            0,
        )
    connection.execute(
        "INSERT INTO legacy_partial_reservations "
        "SELECT r.reservation_identity, c.commit_identity "
        "FROM consumed_reservations r LEFT JOIN commits c "
        "ON c.reservation_identity = r.reservation_identity"
    )
    connection.execute(
        "UPDATE store_format SET version = ?", (_FORMAT_VERSION,)
    )


__all__ = [
    "_FORMAT",
    "_FORMAT_VERSION",
    "_SCHEMA",
    "_SCHEMA_SQL_BY_TABLE",
    "_TABLES",
    "_migrate_v2_store",
    "_migrate_v3_store",
]
