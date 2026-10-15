"""Durable SQLite reservation and atomic commit for pure-action execution."""

from __future__ import annotations

import hashlib
import os
import sqlite3
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
)
from projectkoios.workflow.runtime.pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceAuthority,
    ExperimentalWorkflowPureActionInputSourceAuthorityIdentity,
)
from projectkoios.workflow.runtime.pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceEvidenceIdentity,
)
from projectkoios.workflow.runtime.pure_action_reservation import (
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionCurrentPredecessor,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationRepository,
    ExperimentalWorkflowPureActionReserveStatus,
    ExperimentalWorkflowPureActionRevalidationStatus,
)
from projectkoios.workflow.runtime.pure_action_source_repository import (
    ExperimentalWorkflowPureActionInputSourceReferenceIdentity,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)

_FORMAT = "projectkoios.workflow.experimental-pure-action-store"
_FORMAT_VERSION = 1
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
    "successor_revision INTEGER NOT NULL, record_digest BLOB NOT NULL)",
    "CREATE TABLE commit_source_authorities ("
    "commit_identity TEXT NOT NULL, ordinal INTEGER NOT NULL, "
    "authority_identity TEXT NOT NULL, reference_identity TEXT NOT NULL, "
    "revision_identity TEXT NOT NULL, evidence_identity TEXT NOT NULL, "
    "PRIMARY KEY (commit_identity, ordinal), "
    "FOREIGN KEY (commit_identity) REFERENCES commits (commit_identity))",
)
_TABLES = (
    "active_reservations",
    "commit_source_authorities",
    "commits",
    "consumed_reservations",
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
}


class _StoreFault(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _before_transaction_commit(
    operation: str,
    connection: sqlite3.Connection,
) -> None:
    """Fault-injection seam immediately before the durable commit point."""
    del operation, connection


@final
@dataclass(frozen=True, slots=True)
class ExperimentalSQLitePureActionReservationRepository(
    ExperimentalWorkflowPureActionReservationRepository
):
    """Purpose-built durable repository for pure-action predecessor commits."""

    database_path: Path
    predecessors: tuple[
        ExperimentalWorkflowPureActionCurrentPredecessor, ...
    ] = ()
    busy_timeout_ms: int = 5_000

    def __post_init__(self) -> None:
        if not isinstance(self.database_path, Path):
            raise TypeError("database_path must be pathlib.Path")
        if not self.database_path.is_absolute():
            raise ValueError("database_path must be absolute")
        object.__setattr__(
            self,
            "database_path",
            self.database_path.parent.resolve(strict=False)
            / self.database_path.name,
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
        if type(self.busy_timeout_ms) is not int:
            raise TypeError("busy_timeout_ms must be a built-in int")
        if not 0 <= self.busy_timeout_ms <= 2_147_483_647:
            raise ValueError("busy_timeout_ms is outside its bound")

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
                if existing == (validated_coordinates, validated_record):
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
                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        ]
        | None
    ):
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
            return _load_commit_pair(connection, reservation_identity)
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

    def _prepare(self, connection: sqlite3.Connection) -> None:
        connection.execute("BEGIN IMMEDIATE")
        transaction_open = True
        try:
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


def _reconstruct_reservation(
    value: ExperimentalWorkflowPureActionReservation,
) -> ExperimentalWorkflowPureActionReservation:
    if type(value) is not ExperimentalWorkflowPureActionReservation:
        raise TypeError(
            "reservation must be ExperimentalWorkflowPureActionReservation"
        )
    reconstructed = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=value.execution_plan_identity,
        execution_bindings_identity=value.execution_bindings_identity,
        selected_binding_evidence_identity=value.selected_binding_evidence_identity,
        request_identity=value.request_identity,
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        occurrence_identity=value.occurrence_identity,
        attempt_identity=value.attempt_identity,
        attempt_ordinal=value.attempt_ordinal,
        input_admission_identity=value.input_admission_identity,
        input_authorization_identity=value.input_authorization_identity,
        cpn_plan_identity=value.cpn_plan_identity,
    )
    if reconstructed != value:
        raise ValueError("reservation differs after validation")
    return reconstructed


def _reconstruct_coordinates(
    value: ExperimentalWorkflowPureActionCommitCoordinates,
) -> ExperimentalWorkflowPureActionCommitCoordinates:
    if type(value) is not ExperimentalWorkflowPureActionCommitCoordinates:
        raise TypeError(
            "coordinates must be "
            "ExperimentalWorkflowPureActionCommitCoordinates"
        )
    reconstructed = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=value.commit_identity,
        reservation_identity=value.reservation_identity,
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        successor_marking_identity=value.successor_marking_identity,
        successor_revision=value.successor_revision,
    )
    if reconstructed != value:
        raise ValueError("commit coordinates differ after validation")
    return reconstructed


def _reconstruct_record(
    value: ExperimentalWorkflowPureActionCommitRecord,
) -> ExperimentalWorkflowPureActionCommitRecord:
    if type(value) is not ExperimentalWorkflowPureActionCommitRecord:
        raise TypeError(
            "record must be ExperimentalWorkflowPureActionCommitRecord"
        )
    reconstructed = ExperimentalWorkflowPureActionCommitRecord(
        commit_identity=value.commit_identity,
        cpn_plan_identity=value.cpn_plan_identity,
        reservation_identity=value.reservation_identity,
        input_authorization_identity=value.input_authorization_identity,
        source_authorities=value.source_authorities,
        invocation_outcome_identity=value.invocation_outcome_identity,
        request_identity=value.request_identity,
        owner_result_identity=value.owner_result_identity,
        mapped_result_identity=value.mapped_result_identity,
        firing_outcome_identity=value.firing_outcome_identity,
        cpn_firing_result_identity=value.cpn_firing_result_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        successor_marking_identity=value.successor_marking_identity,
        successor_revision=value.successor_revision,
    )
    if reconstructed != value:
        raise ValueError("commit record differs after validation")
    return reconstructed


def _validate_commit_correlations(
    reservation: ExperimentalWorkflowPureActionReservation,
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
    record: ExperimentalWorkflowPureActionCommitRecord,
) -> None:
    if (
        coordinates.reservation_identity != reservation.identity
        or coordinates.net_instance_identity
        != reservation.net_instance_identity
        or coordinates.predecessor_marking_identity
        != reservation.predecessor_marking_identity
        or coordinates.predecessor_revision != reservation.predecessor_revision
        or record.commit_identity != coordinates.commit_identity
        or record.reservation_identity != reservation.identity
        or record.cpn_plan_identity != reservation.cpn_plan_identity
        or record.input_authorization_identity
        != reservation.input_authorization_identity
        or record.predecessor_marking_identity
        != coordinates.predecessor_marking_identity
        or record.predecessor_revision != coordinates.predecessor_revision
        or record.successor_marking_identity
        != coordinates.successor_marking_identity
        or record.successor_revision != coordinates.successor_revision
    ):
        raise ValueError("commit state differs from reservation")


def _reservation_values(
    value: ExperimentalWorkflowPureActionReservation,
) -> tuple[object, ...]:
    return (
        value.identity.value,
        value.execution_plan_identity.value,
        value.execution_bindings_identity.value,
        value.selected_binding_evidence_identity.value,
        value.request_identity.value,
        value.net_instance_identity.value,
        value.predecessor_marking_identity.value,
        value.predecessor_revision,
        value.occurrence_identity.value,
        value.attempt_identity.value,
        value.attempt_ordinal,
        None
        if value.input_admission_identity is None
        else value.input_admission_identity.value,
        None
        if value.input_authorization_identity is None
        else value.input_authorization_identity.value,
        None
        if value.cpn_plan_identity is None
        else value.cpn_plan_identity.value,
    )


def _reservation_from_row(
    row: tuple[object, ...],
) -> ExperimentalWorkflowPureActionReservation:
    if len(row) != 14:
        raise _StoreFault("invalid_reservation_shape")
    identity = _required_text(row[0], "reservation_identity")
    admission = _optional_text(row[11], "input_admission_identity")
    authorization = _optional_text(row[12], "input_authorization_identity")
    cpn_plan = _optional_text(row[13], "cpn_plan_identity")
    try:
        reservation = ExperimentalWorkflowPureActionReservation(
            execution_plan_identity=ExperimentalWorkflowPureActionExecutionPlanIdentity(
                _required_text(row[1], "execution_plan_identity")
            ),
            execution_bindings_identity=ExperimentalWorkflowPureActionExecutionBindingsIdentity(
                _required_text(row[2], "execution_bindings_identity")
            ),
            selected_binding_evidence_identity=ExperimentalWorkflowSelectedBindingEvidenceIdentity(
                _required_text(row[3], "selected_binding_evidence_identity")
            ),
            request_identity=WorkflowFiringRequestIdentity(
                _required_text(row[4], "request_identity")
            ),
            net_instance_identity=WorkflowNetInstanceIdentity(
                _required_text(row[5], "net_instance_identity")
            ),
            predecessor_marking_identity=WorkflowMarkingIdentity(
                _required_text(row[6], "predecessor_marking_identity")
            ),
            predecessor_revision=_required_int(row[7], "predecessor_revision"),
            occurrence_identity=WorkflowOccurrenceIdentity(
                _required_text(row[8], "occurrence_identity")
            ),
            attempt_identity=WorkflowAttemptIdentity(
                _required_text(row[9], "attempt_identity")
            ),
            attempt_ordinal=_required_int(row[10], "attempt_ordinal"),
            input_admission_identity=(
                None
                if admission is None
                else ExperimentalWorkflowPureActionAdmittedInputsIdentity(
                    admission
                )
            ),
            input_authorization_identity=(
                None
                if authorization is None
                else ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                    authorization
                )
            ),
            cpn_plan_identity=(
                None
                if cpn_plan is None
                else ExperimentalWorkflowPureActionCpnPlanIdentity(cpn_plan)
            ),
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_reservation") from error
    if reservation.identity.value != identity:
        raise _StoreFault("reservation_identity_mismatch")
    return reservation


def _commit_values(
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
    record: ExperimentalWorkflowPureActionCommitRecord,
    net_instance_identity: WorkflowNetInstanceIdentity,
) -> tuple[object, ...]:
    return (
        record.reservation_identity.value,
        record.commit_identity.value,
        net_instance_identity.value,
        record.cpn_plan_identity.value,
        record.input_authorization_identity.value,
        record.invocation_outcome_identity,
        record.request_identity.value,
        record.owner_result_identity.value,
        record.mapped_result_identity,
        record.firing_outcome_identity,
        record.cpn_firing_result_identity,
        coordinates.predecessor_marking_identity.value,
        coordinates.predecessor_revision,
        coordinates.successor_marking_identity.value,
        coordinates.successor_revision,
        _record_digest(record, net_instance_identity),
    )


def _load_commit_pair(
    connection: sqlite3.Connection,
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
) -> (
    tuple[
        ExperimentalWorkflowPureActionCommitCoordinates,
        ExperimentalWorkflowPureActionCommitRecord,
    ]
    | None
):
    row = connection.execute(
        "SELECT * FROM commits WHERE reservation_identity = ?",
        (reservation_identity.value,),
    ).fetchone()
    if row is None:
        return None
    if len(row) != 16:
        raise _StoreFault("invalid_commit_shape")
    commit_identity = _required_text(row[1], "commit_identity")
    authority_rows = connection.execute(
        "SELECT ordinal, authority_identity, reference_identity, "
        "revision_identity, evidence_identity "
        "FROM commit_source_authorities WHERE commit_identity = ? "
        "ORDER BY ordinal",
        (commit_identity,),
    ).fetchall()
    authorities = tuple(
        _authority_from_row(tuple(authority_row), expected_ordinal)
        for expected_ordinal, authority_row in enumerate(authority_rows)
    )
    try:
        record = ExperimentalWorkflowPureActionCommitRecord(
            commit_identity=ExperimentalWorkflowPureActionCommitIdentity(
                commit_identity
            ),
            cpn_plan_identity=ExperimentalWorkflowPureActionCpnPlanIdentity(
                _required_text(row[3], "cpn_plan_identity")
            ),
            reservation_identity=ExperimentalWorkflowPureActionReservationIdentity(
                _required_text(row[0], "reservation_identity")
            ),
            input_authorization_identity=ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                _required_text(row[4], "input_authorization_identity")
            ),
            source_authorities=authorities,
            invocation_outcome_identity=_required_text(
                row[5], "invocation_outcome_identity"
            ),
            request_identity=WorkflowFiringRequestIdentity(
                _required_text(row[6], "request_identity")
            ),
            owner_result_identity=WorkflowFiringResultIdentity(
                _required_text(row[7], "owner_result_identity")
            ),
            mapped_result_identity=_required_text(
                row[8], "mapped_result_identity"
            ),
            firing_outcome_identity=_required_text(
                row[9], "firing_outcome_identity"
            ),
            cpn_firing_result_identity=_required_text(
                row[10], "cpn_firing_result_identity"
            ),
            predecessor_marking_identity=WorkflowMarkingIdentity(
                _required_text(row[11], "predecessor_marking_identity")
            ),
            predecessor_revision=_required_int(row[12], "predecessor_revision"),
            successor_marking_identity=WorkflowMarkingIdentity(
                _required_text(row[13], "successor_marking_identity")
            ),
            successor_revision=_required_int(row[14], "successor_revision"),
        )
        net_instance = WorkflowNetInstanceIdentity(
            _required_text(row[2], "net_instance_identity")
        )
        coordinates = ExperimentalWorkflowPureActionCommitCoordinates(
            commit_identity=record.commit_identity,
            reservation_identity=record.reservation_identity,
            net_instance_identity=net_instance,
            predecessor_marking_identity=record.predecessor_marking_identity,
            predecessor_revision=record.predecessor_revision,
            successor_marking_identity=record.successor_marking_identity,
            successor_revision=record.successor_revision,
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_commit") from error
    digest = row[15]
    if type(digest) is not bytes or digest != _record_digest(
        record, net_instance
    ):
        raise _StoreFault("commit_record_digest_mismatch")
    if record.reservation_identity != reservation_identity:
        raise _StoreFault("commit_reservation_mismatch")
    return coordinates, record


def _authority_from_row(
    row: tuple[object, ...],
    expected_ordinal: int,
) -> ExperimentalWorkflowPureActionInputSourceAuthority:
    if (
        len(row) != 5
        or _required_int(row[0], "authority_ordinal") != expected_ordinal
    ):
        raise _StoreFault("invalid_source_authority_order")
    identity = _required_text(row[1], "authority_identity")
    try:
        authority = ExperimentalWorkflowPureActionInputSourceAuthority(
            reference_identity=ExperimentalWorkflowPureActionInputSourceReferenceIdentity(
                _required_text(row[2], "reference_identity")
            ),
            revision_identity=ExperimentalWorkflowPureActionInputSourceRevisionIdentity(
                _required_text(row[3], "revision_identity")
            ),
            evidence_identity=ExperimentalWorkflowPureActionInputSourceEvidenceIdentity(
                _required_text(row[4], "evidence_identity")
            ),
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_source_authority") from error
    if (
        authority.identity
        != ExperimentalWorkflowPureActionInputSourceAuthorityIdentity(identity)
    ):
        raise _StoreFault("source_authority_identity_mismatch")
    return authority


def _predecessor_from_row(
    row: tuple[object, ...],
) -> ExperimentalWorkflowPureActionCurrentPredecessor:
    if len(row) != 4:
        raise _StoreFault("invalid_predecessor_shape")
    try:
        predecessor = ExperimentalWorkflowPureActionCurrentPredecessor(
            net_instance_identity=WorkflowNetInstanceIdentity(
                _required_text(row[0], "net_instance_identity")
            ),
            marking_identity=WorkflowMarkingIdentity(
                _required_text(row[1], "marking_identity")
            ),
            revision=_required_int(row[2], "revision"),
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_predecessor") from error
    digest = row[3]
    if type(digest) is not bytes or digest != _predecessor_digest(
        predecessor.net_instance_identity,
        predecessor.marking_identity,
        predecessor.revision,
    ):
        raise _StoreFault("predecessor_digest_mismatch")
    return predecessor


def _predecessor_digest(
    net_instance_identity: WorkflowNetInstanceIdentity,
    marking_identity: WorkflowMarkingIdentity,
    revision: int,
) -> bytes:
    digest = hashlib.sha256(
        b"projectkoios.workflow.experimental-current-predecessor:0\x00"
    )
    for value in (
        net_instance_identity.value,
        marking_identity.value,
        str(revision),
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.digest()


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


def _record_digest(
    record: ExperimentalWorkflowPureActionCommitRecord,
    net_instance_identity: WorkflowNetInstanceIdentity,
) -> bytes:
    digest = hashlib.sha256(
        b"projectkoios.workflow.experimental-pure-action-commit-record:0\x00"
    )
    for value in (
        record.commit_identity.value,
        record.cpn_plan_identity.value,
        record.reservation_identity.value,
        record.input_authorization_identity.value,
        net_instance_identity.value,
        record.invocation_outcome_identity,
        record.request_identity.value,
        record.owner_result_identity.value,
        record.mapped_result_identity,
        record.firing_outcome_identity,
        record.cpn_firing_result_identity,
        record.predecessor_marking_identity.value,
        str(record.predecessor_revision),
        record.successor_marking_identity.value,
        str(record.successor_revision),
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    for authority in record.source_authorities:
        for value in (
            authority.identity.value,
            authority.reference_identity.value,
            authority.revision_identity.value,
            authority.evidence_identity.value,
        ):
            encoded = value.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
    return digest.digest()


def _required_text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise _StoreFault(f"invalid_{label}")
    return value


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)


def _required_int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise _StoreFault(f"invalid_{label}")
    return value


def _rollback(connection: sqlite3.Connection) -> None:
    connection.execute("ROLLBACK")


def _rollback_quietly(connection: sqlite3.Connection) -> None:
    try:
        _rollback(connection)
    except sqlite3.Error:
        pass


__all__ = ["ExperimentalSQLitePureActionReservationRepository"]
