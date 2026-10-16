"""SQLite row codec for canonical reservation lifecycle events."""

from __future__ import annotations

import hashlib
import sqlite3

from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionReservationLifecycleEvent,
    ExperimentalWorkflowPureActionReservationLifecycleJsonCodec,
    ExperimentalWorkflowPureActionReservationLifecycleState,
)

from ._sqlite_private import SQLiteStoreFault as _StoreFault


def _insert_lifecycle_event(
    connection: sqlite3.Connection,
    event: ExperimentalWorkflowPureActionReservationLifecycleEvent,
    ordinal: int,
) -> None:
    encoded = (
        ExperimentalWorkflowPureActionReservationLifecycleJsonCodec().encode(
            event
        )
    )
    connection.execute(
        "INSERT INTO reservation_lifecycle_events VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            event.reservation.identity.value,
            ordinal,
            event.identity.value,
            event.state.value,
            None
            if event.commit_identity is None
            else event.commit_identity.value,
            encoded,
            hashlib.sha256(encoded).digest(),
        ),
    )


def _load_lifecycle_events(
    connection: sqlite3.Connection,
    reservation_identity: str,
) -> tuple[ExperimentalWorkflowPureActionReservationLifecycleEvent, ...]:
    rows = connection.execute(
        "SELECT ordinal, lifecycle_identity, state, commit_identity, "
        "event_bytes, event_digest FROM reservation_lifecycle_events "
        "WHERE reservation_identity = ? ORDER BY ordinal",
        (reservation_identity,),
    ).fetchall()
    events: list[ExperimentalWorkflowPureActionReservationLifecycleEvent] = []
    codec = ExperimentalWorkflowPureActionReservationLifecycleJsonCodec()
    for expected_ordinal, row in enumerate(rows):
        if len(row) != 6 or row[0] != expected_ordinal:
            raise _StoreFault("invalid_reservation_lifecycle_sequence")
        encoded, digest = row[4], row[5]
        if type(encoded) is not bytes or type(digest) is not bytes:
            raise _StoreFault("invalid_reservation_lifecycle_bytes")
        if hashlib.sha256(encoded).digest() != digest:
            raise _StoreFault("reservation_lifecycle_digest_mismatch")
        try:
            event = codec.decode(encoded)
        except (TypeError, ValueError) as error:
            raise _StoreFault("invalid_reservation_lifecycle_event") from error
        retained_commit = (
            None
            if event.commit_identity is None
            else event.commit_identity.value
        )
        if (
            event.reservation.identity.value != reservation_identity
            or event.identity.value != row[1]
            or event.state.value != row[2]
            or retained_commit != row[3]
        ):
            raise _StoreFault("reservation_lifecycle_row_mismatch")
        events.append(event)
    result = tuple(events)
    if result:
        lifecycle_state = (
            ExperimentalWorkflowPureActionReservationLifecycleState
        )
        if result[0].state is not lifecycle_state.RESERVED:
            raise _StoreFault("invalid_reservation_lifecycle_sequence")
        if len(result) > 2 or (
            len(result) == 2
            and result[1].state is not lifecycle_state.COMMITTED
        ):
            raise _StoreFault("invalid_reservation_lifecycle_sequence")
        commit_row = connection.execute(
            "SELECT commit_identity FROM commits "
            "WHERE reservation_identity = ?",
            (reservation_identity,),
        ).fetchone()
        if len(result) == 1:
            retained_commit = None
        else:
            commit_identity = result[1].commit_identity
            if commit_identity is None:
                raise _StoreFault("invalid_reservation_lifecycle_sequence")
            retained_commit = commit_identity.value
        database_commit = None if commit_row is None else commit_row[0]
        if retained_commit != database_commit:
            raise _StoreFault("reservation_lifecycle_commit_mismatch")
    return result


__all__ = ["_insert_lifecycle_event", "_load_lifecycle_events"]
