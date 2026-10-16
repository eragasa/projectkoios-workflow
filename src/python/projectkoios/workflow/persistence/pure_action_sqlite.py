"""Durable SQLite reservation and atomic commit for pure-action execution."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import final

from projectkoios.workflow.execution.pure_action_cpn_replay_evidence import (
    ExperimentalWorkflowPureActionCpnReplayEvidence,
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult,
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus,
)
from projectkoios.workflow.execution.pure_action_cpn_replay_repository import (
    ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
)
from projectkoios.workflow.runtime.pure_action_commit_serialization import (
    ExperimentalWorkflowPureActionCommitEventJsonCodec,
)
from projectkoios.workflow.runtime.pure_action_reservation import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitReadResult,
    ExperimentalWorkflowPureActionCommitReadStatus,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCommittedSnapshot,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationRepository,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowNetInstanceIdentity,
)

from ._pure_action_cpn_replay_sqlite_rows import (
    _insert_replay_evidence,
    _load_replay_evidence_pair,
    _reconstruct_replay_evidence,
)
from ._pure_action_sqlite_rows import (
    _commit_from_rows,
    _commit_identity_from_row,
    _commit_values,
    _predecessor_digest,
    _predecessor_from_row,
    _reconstruct_coordinates,
    _reconstruct_record,
    _reconstruct_reservation,
    _reservation_from_row,
    _reservation_values,
    _validate_commit_correlations,
)
from ._sqlite_private import (
    SQLiteStoreFault as _StoreFault,
)
from ._sqlite_private import (
    canonical_database_path,
    connect_private_database,
    prepare_store_schema,
    validate_busy_timeout,
)
from ._sqlite_private import (
    rollback_quietly as _rollback_quietly,
)

_FORMAT = "projectkoios.workflow.experimental-pure-action-store"
_FORMAT_VERSION = 3
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
_TABLES = (
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
}


def _before_transaction_commit(
    operation: str,
    connection: sqlite3.Connection,
) -> None:
    """Fault-injection seam immediately before the durable commit point."""
    del operation, connection


@final
@dataclass(frozen=True, slots=True)
class ExperimentalSQLitePureActionReservationRepository(
    ExperimentalWorkflowPureActionReservationRepository,
    ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
):
    """Purpose-built durable repository for pure-action predecessor commits."""

    database_path: Path
    predecessors: tuple[
        ExperimentalWorkflowPureActionCurrentPredecessor, ...
    ] = ()
    busy_timeout_ms: int = 5_000

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "database_path",
            canonical_database_path(self.database_path),
        )
        if type(self.predecessors) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCurrentPredecessor
            for item in self.predecessors
        ):
            raise TypeError(
                "predecessors must contain current predecessor records"
            )
        net_instances = tuple(
            item.net_instance_identity for item in self.predecessors
        )
        if len(net_instances) != len(set(net_instances)):
            raise ValueError("current predecessor net instances must be unique")
        validate_busy_timeout(self.busy_timeout_ms)

    def reserve(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionReserveStatus:
        """Durably reserve one exact current predecessor."""
        validated = _reconstruct_reservation(reservation)
        connection: sqlite3.Connection | None = None
        transaction_open = False
        phase = "open"
        try:
            connection = self._connect()
            phase = "prepare"
            self._prepare(connection)
            phase = "compare"
            connection.execute("BEGIN IMMEDIATE")
            transaction_open = True
            if not _matches_current(connection, validated):
                _rollback(connection)
                transaction_open = False
                return ExperimentalWorkflowPureActionReserveStatus.STALE
            row = connection.execute(
                "SELECT * FROM active_reservations "
                "WHERE net_instance_identity = ?",
                (validated.net_instance_identity.value,),
            ).fetchone()
            if row is not None:
                existing = _reservation_from_row(tuple(row))
                _rollback(connection)
                transaction_open = False
                if existing == validated:
                    return (
                        ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT
                    )
                return ExperimentalWorkflowPureActionReserveStatus.CONFLICT
            consumed = connection.execute(
                "SELECT 1 FROM consumed_reservations "
                "WHERE reservation_identity = ?",
                (validated.identity.value,),
            ).fetchone()
            if consumed is not None:
                _rollback(connection)
                transaction_open = False
                return ExperimentalWorkflowPureActionReserveStatus.CONFLICT
            connection.execute(
                "INSERT INTO active_reservations VALUES "
                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _reservation_values(validated),
            )
            phase = "precommit"
            _before_transaction_commit("reserve", connection)
            phase = "acknowledge"
            connection.execute("COMMIT")
            transaction_open = False
            return ExperimentalWorkflowPureActionReserveStatus.RESERVED
        except OSError, sqlite3.Error, _StoreFault, RuntimeError:
            return (
                ExperimentalWorkflowPureActionReserveStatus.INDETERMINATE
                if phase == "acknowledge"
                else ExperimentalWorkflowPureActionReserveStatus.ERROR
            )
        finally:
            if connection is not None:
                if transaction_open:
                    _rollback_quietly(connection)
                connection.close()

    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        """Read the durable status of one exact reservation."""
        validated = _reconstruct_reservation(reservation)
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            self._prepare(connection)
            connection.execute("BEGIN")
            consumed = connection.execute(
                "SELECT 1 FROM consumed_reservations "
                "WHERE reservation_identity = ?",
                (validated.identity.value,),
            ).fetchone()
            if consumed is not None:
                return ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
            row = connection.execute(
                "SELECT * FROM active_reservations "
                "WHERE net_instance_identity = ?",
                (validated.net_instance_identity.value,),
            ).fetchone()
            if row is None or _reservation_from_row(tuple(row)) != validated:
                return ExperimentalWorkflowPureActionRevalidationStatus.ABSENT
            if not _matches_current(connection, validated):
                return ExperimentalWorkflowPureActionRevalidationStatus.STALE
            return ExperimentalWorkflowPureActionRevalidationStatus.CURRENT
        except OSError, sqlite3.Error, _StoreFault:
            return ExperimentalWorkflowPureActionRevalidationStatus.ERROR
        finally:
            if connection is not None:
                connection.close()

    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Retain a legacy compact commit without CPN replay evidence."""
        return self._commit(reservation, coordinates, record, None)

    def commit_with_cpn_replay(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord,
        evidence: ExperimentalWorkflowPureActionCpnReplayEvidence,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically retain compact commit state and exact replay evidence."""
        if (
            type(evidence)
            is not ExperimentalWorkflowPureActionCpnReplayEvidence
        ):
            raise TypeError(
                "evidence must be "
                "ExperimentalWorkflowPureActionCpnReplayEvidence"
            )
        return self._commit(reservation, coordinates, record, evidence)

    def _commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None,
        evidence: ExperimentalWorkflowPureActionCpnReplayEvidence | None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Retain, consume, and advance in one durable transaction."""
        validated_reservation = _reconstruct_reservation(reservation)
        validated_coordinates = _reconstruct_coordinates(coordinates)
        if record is None:
            raise ValueError(
                "durable commit requires the complete commit record"
            )
        validated_record = _reconstruct_record(record)
        _validate_commit_correlations(
            validated_reservation,
            validated_coordinates,
            validated_record,
        )
        validated_evidence = (
            None if evidence is None else _reconstruct_replay_evidence(evidence)
        )
        if validated_evidence is not None and (
            validated_evidence.commit_identity
            != validated_record.commit_identity
            or validated_evidence.cpn_plan_identity
            != validated_record.cpn_plan_identity
            or validated_evidence.cpn_firing_result_identity
            != validated_record.cpn_firing_result_identity
            or validated_evidence.predecessor_marking_identity
            != validated_record.predecessor_marking_identity
            or validated_evidence.successor_marking_identity
            != validated_record.successor_marking_identity
        ):
            raise ValueError("CPN replay evidence differs from compact commit")
        connection: sqlite3.Connection | None = None
        transaction_open = False
        phase = "open"
        try:
            connection = self._connect()
            phase = "prepare"
            self._prepare(connection)
            phase = "compare"
            connection.execute("BEGIN IMMEDIATE")
            transaction_open = True
            existing = _load_commit_pair(
                connection,
                validated_reservation.identity,
            )
            if existing is not None:
                _rollback(connection)
                transaction_open = False
                if existing == (
                    validated_coordinates,
                    validated_record,
                    ExperimentalWorkflowPureActionCommitEventJsonCodec().encode(
                        validated_record
                    ),
                ) and (
                    validated_evidence is None
                    or _load_replay_evidence_pair(
                        connection,
                        validated_record.commit_identity,
                    )
                    == validated_evidence
                ):
                    return ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            collision = connection.execute(
                "SELECT 1 FROM commits WHERE commit_identity = ?",
                (validated_coordinates.commit_identity.value,),
            ).fetchone()
            if collision is not None:
                _rollback(connection)
                transaction_open = False
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            if not _matches_current(connection, validated_reservation):
                _rollback(connection)
                transaction_open = False
                return ExperimentalWorkflowPureActionCommitStatus.STALE
            active_row = connection.execute(
                "SELECT * FROM active_reservations "
                "WHERE net_instance_identity = ?",
                (validated_reservation.net_instance_identity.value,),
            ).fetchone()
            if (
                active_row is None
                or _reservation_from_row(tuple(active_row))
                != validated_reservation
            ):
                _rollback(connection)
                transaction_open = False
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            connection.execute(
                "INSERT INTO commits VALUES "
                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                _commit_values(
                    validated_coordinates,
                    validated_record,
                    validated_reservation.net_instance_identity,
                ),
            )
            for ordinal, authority in enumerate(
                validated_record.source_authorities
            ):
                connection.execute(
                    "INSERT INTO commit_source_authorities VALUES "
                    "(?, ?, ?, ?, ?, ?)",
                    (
                        validated_record.commit_identity.value,
                        ordinal,
                        authority.identity.value,
                        authority.reference_identity.value,
                        authority.revision_identity.value,
                        authority.evidence_identity.value,
                    ),
                )
            if validated_evidence is not None:
                _insert_replay_evidence(connection, validated_evidence)
            connection.execute(
                "INSERT INTO consumed_reservations VALUES (?)",
                (validated_reservation.identity.value,),
            )
            connection.execute(
                "DELETE FROM active_reservations "
                "WHERE reservation_identity = ?",
                (validated_reservation.identity.value,),
            )
            updated = connection.execute(
                "UPDATE current_predecessors SET marking_identity = ?, "
                "revision = ?, coordinate_digest = ? "
                "WHERE net_instance_identity = ? "
                "AND marking_identity = ? AND revision = ?",
                (
                    validated_coordinates.successor_marking_identity.value,
                    validated_coordinates.successor_revision,
                    _predecessor_digest(
                        validated_reservation.net_instance_identity,
                        validated_coordinates.successor_marking_identity,
                        validated_coordinates.successor_revision,
                    ),
                    validated_reservation.net_instance_identity.value,
                    validated_coordinates.predecessor_marking_identity.value,
                    validated_coordinates.predecessor_revision,
                ),
            )
            if updated.rowcount != 1:
                _rollback(connection)
                transaction_open = False
                return ExperimentalWorkflowPureActionCommitStatus.STALE
            phase = "precommit"
            _before_transaction_commit("commit", connection)
            phase = "acknowledge"
            connection.execute("COMMIT")
            transaction_open = False
            return ExperimentalWorkflowPureActionCommitStatus.COMMITTED
        except OSError, sqlite3.Error, _StoreFault, RuntimeError:
            return (
                ExperimentalWorkflowPureActionCommitStatus.INDETERMINATE
                if phase == "acknowledge"
                else ExperimentalWorkflowPureActionCommitStatus.ERROR
            )
        finally:
            if connection is not None:
                if transaction_open:
                    _rollback_quietly(connection)
                connection.close()

    def load_committed_snapshot(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitReadResult:
        """Atomically load and classify one durable committed snapshot."""
        if type(reservation_identity) is not (
            ExperimentalWorkflowPureActionReservationIdentity
        ):
            raise TypeError(
                "reservation_identity must be "
                "ExperimentalWorkflowPureActionReservationIdentity"
            )
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            self._prepare(connection)
            loaded = _load_commit_pair(connection, reservation_identity)
            if loaded is None:
                return _commit_read_failure(
                    ExperimentalWorkflowPureActionCommitReadStatus.ABSENT,
                    "commit_absent",
                )
            coordinates, record, event = loaded
            snapshot = ExperimentalWorkflowPureActionCommittedSnapshot(
                coordinates=coordinates,
                record=record,
                event_bytes=event,
            )
            return ExperimentalWorkflowPureActionCommitReadResult(
                status=ExperimentalWorkflowPureActionCommitReadStatus.FOUND,
                snapshot=snapshot,
                diagnostics=(),
            )
        except TypeError, ValueError:
            return _commit_read_failure(
                ExperimentalWorkflowPureActionCommitReadStatus.CORRUPT,
                "commit_snapshot_invalid",
            )
        except _StoreFault as error:
            return _commit_read_failure(
                _commit_read_fault_status(error.code),
                error.code,
            )
        except OSError, sqlite3.Error:
            return _commit_read_failure(
                ExperimentalWorkflowPureActionCommitReadStatus.ERROR,
                "sqlite_read_failed",
            )
        finally:
            if connection is not None:
                connection.close()

    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load verified durable commit coordinates."""
        loaded = self._load_commit(reservation_identity)
        return None if loaded is None else loaded[0]

    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the verified complete compact durable commit record."""
        loaded = self._load_commit(reservation_identity)
        return None if loaded is None else loaded[1]

    def load_commit_event(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> bytes | None:
        """Load exact verified canonical committed-event bytes."""
        loaded = self._load_commit(reservation_identity)
        if loaded is None:
            return None
        _, record, event = loaded
        if (
            ExperimentalWorkflowPureActionCommitEventJsonCodec().decode(event)
            != record
        ):
            raise RuntimeError("commit_event_record_mismatch")
        return event

    def load_cpn_replay_evidence(
        self,
        commit_identity: ExperimentalWorkflowPureActionCommitIdentity,
    ) -> ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult:
        """Atomically load and classify exact durable CPN replay evidence."""
        if (
            type(commit_identity)
            is not ExperimentalWorkflowPureActionCommitIdentity
        ):
            raise TypeError(
                "commit_identity must be "
                "ExperimentalWorkflowPureActionCommitIdentity"
            )
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            self._prepare(connection)
            evidence = _load_replay_evidence_pair(connection, commit_identity)
            if evidence is None:
                return _replay_read_failure(
                    ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.ABSENT,
                    "cpn_replay_evidence_absent",
                )
            return ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult(
                status=ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.FOUND,
                evidence=evidence,
                diagnostics=(),
            )
        except _StoreFault as error:
            read_status = (
                ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus
            )
            if error.code == "unsupported_store_version":
                status = read_status.INCOMPATIBLE
            elif error.code.startswith("invalid_") or error.code.endswith(
                "_mismatch"
            ):
                status = read_status.CORRUPT
            else:
                status = read_status.ERROR
            return _replay_read_failure(status, error.code)
        except TypeError, ValueError:
            return _replay_read_failure(
                ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.CORRUPT,
                "cpn_replay_evidence_invalid",
            )
        except OSError, sqlite3.Error:
            return _replay_read_failure(
                ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.ERROR,
                "sqlite_read_failed",
            )
        finally:
            if connection is not None:
                connection.close()

    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the verified durable current predecessor coordinate."""
        if type(net_instance_identity) is not WorkflowNetInstanceIdentity:
            raise TypeError(
                "net_instance_identity must be WorkflowNetInstanceIdentity"
            )
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            self._prepare(connection)
            row = connection.execute(
                "SELECT net_instance_identity, marking_identity, revision, "
                "coordinate_digest FROM current_predecessors "
                "WHERE net_instance_identity = ?",
                (net_instance_identity.value,),
            ).fetchone()
            if row is None:
                return None
            return _predecessor_from_row(tuple(row))
        except (OSError, sqlite3.Error, _StoreFault) as error:
            code = (
                error.code
                if isinstance(error, _StoreFault)
                else "sqlite_read_failed"
            )
            raise RuntimeError(code) from error
        finally:
            if connection is not None:
                connection.close()

    def _load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> (
        tuple[
            ExperimentalWorkflowPureActionCommitCoordinates,
            ExperimentalWorkflowPureActionCommitRecord,
            bytes,
        ]
        | None
    ):
        result = self.load_committed_snapshot(reservation_identity)
        if (
            result.status
            is ExperimentalWorkflowPureActionCommitReadStatus.ABSENT
        ):
            return None
        if (
            result.status
            is not ExperimentalWorkflowPureActionCommitReadStatus.FOUND
        ):
            raise RuntimeError(result.diagnostics[0])
        assert result.snapshot is not None
        return (
            result.snapshot.coordinates,
            result.snapshot.record,
            result.snapshot.event_bytes,
        )

    def _connect(self) -> sqlite3.Connection:
        return connect_private_database(
            self.database_path,
            self.busy_timeout_ms,
        )

    def _prepare(self, connection: sqlite3.Connection) -> None:
        connection.execute("BEGIN IMMEDIATE")
        transaction_open = True
        try:
            _migrate_v2_store(connection)
            prepare_store_schema(
                connection,
                schema=_SCHEMA,
                tables=_TABLES,
                schema_sql_by_table=_SCHEMA_SQL_BY_TABLE,
                format_identity=_FORMAT,
                format_version=_FORMAT_VERSION,
            )
            for predecessor in self.predecessors:
                row = connection.execute(
                    "SELECT net_instance_identity, marking_identity, revision, "
                    "coordinate_digest FROM initial_predecessors "
                    "WHERE net_instance_identity = ?",
                    (predecessor.net_instance_identity.value,),
                ).fetchone()
                if row is None:
                    current = connection.execute(
                        "SELECT 1 FROM current_predecessors "
                        "WHERE net_instance_identity = ?",
                        (predecessor.net_instance_identity.value,),
                    ).fetchone()
                    if current is not None:
                        raise _StoreFault("missing_initial_predecessor")
                    values = (
                        predecessor.net_instance_identity.value,
                        predecessor.marking_identity.value,
                        predecessor.revision,
                        _predecessor_digest(
                            predecessor.net_instance_identity,
                            predecessor.marking_identity,
                            predecessor.revision,
                        ),
                    )
                    connection.execute(
                        "INSERT INTO initial_predecessors VALUES (?, ?, ?, ?)",
                        values,
                    )
                    connection.execute(
                        "INSERT INTO current_predecessors VALUES (?, ?, ?, ?)",
                        values,
                    )
                elif _predecessor_from_row(tuple(row)) != predecessor:
                    raise _StoreFault("predecessor_bootstrap_conflict")
            connection.execute("COMMIT")
            transaction_open = False
        finally:
            if transaction_open:
                _rollback_quietly(connection)


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
    for statement in _SCHEMA[7:]:
        connection.execute(statement)
    connection.execute(
        "UPDATE store_format SET version = ?", (_FORMAT_VERSION,)
    )


def _replay_read_failure(
    status: ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult:
    return ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult(
        status=status,
        evidence=None,
        diagnostics=(diagnostic,),
    )


def _commit_read_failure(
    status: ExperimentalWorkflowPureActionCommitReadStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCommitReadResult:
    return ExperimentalWorkflowPureActionCommitReadResult(
        status=status,
        snapshot=None,
        diagnostics=(diagnostic,),
    )


def _commit_read_fault_status(
    code: str,
) -> ExperimentalWorkflowPureActionCommitReadStatus:
    if code in {
        "unrecognized_store_objects",
        "unrecognized_store_schema",
        "unsupported_store_version",
    }:
        return ExperimentalWorkflowPureActionCommitReadStatus.INCOMPATIBLE
    if (
        code.startswith("invalid_")
        or code.endswith("_mismatch")
        or code in {"missing_initial_predecessor"}
    ):
        return ExperimentalWorkflowPureActionCommitReadStatus.CORRUPT
    return ExperimentalWorkflowPureActionCommitReadStatus.ERROR


def _load_commit_pair(
    connection: sqlite3.Connection,
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
) -> (
    tuple[
        ExperimentalWorkflowPureActionCommitCoordinates,
        ExperimentalWorkflowPureActionCommitRecord,
        bytes,
    ]
    | None
):
    row = connection.execute(
        "SELECT * FROM commits WHERE reservation_identity = ?",
        (reservation_identity.value,),
    ).fetchone()
    if row is None:
        return None
    commit_row = tuple(row)
    commit_identity = _commit_identity_from_row(commit_row)
    authority_rows = tuple(
        tuple(authority_row)
        for authority_row in connection.execute(
            "SELECT ordinal, authority_identity, reference_identity, "
            "revision_identity, evidence_identity "
            "FROM commit_source_authorities WHERE commit_identity = ? "
            "ORDER BY ordinal",
            (commit_identity,),
        ).fetchall()
    )
    return _commit_from_rows(
        commit_row,
        authority_rows,
        reservation_identity,
    )


def _matches_current(
    connection: sqlite3.Connection,
    reservation: ExperimentalWorkflowPureActionReservation,
) -> bool:
    row = connection.execute(
        "SELECT net_instance_identity, marking_identity, revision, "
        "coordinate_digest FROM current_predecessors "
        "WHERE net_instance_identity = ?",
        (reservation.net_instance_identity.value,),
    ).fetchone()
    if row is None:
        return False
    current = _predecessor_from_row(tuple(row))
    return current == ExperimentalWorkflowPureActionCurrentPredecessor(
        net_instance_identity=reservation.net_instance_identity,
        marking_identity=reservation.predecessor_marking_identity,
        revision=reservation.predecessor_revision,
    )


def _rollback(connection: sqlite3.Connection) -> None:
    connection.execute("ROLLBACK")


__all__ = ["ExperimentalSQLitePureActionReservationRepository"]
