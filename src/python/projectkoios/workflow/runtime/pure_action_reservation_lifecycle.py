"""Canonical identity-only lifecycle history for pure-action reservations."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)

from .pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
)
from .pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
)
from .pure_action_reservation import (
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
)

_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-reservation-lifecycle:0"
)
_SCHEMA = (
    "projectkoios.workflow.experimental-pure-action-reservation-lifecycle:0"
)
_MAX_BYTES = 16_384
_RESERVATION_KEYS = {
    "attempt_identity",
    "attempt_ordinal",
    "cpn_plan_identity",
    "execution_bindings_identity",
    "execution_plan_identity",
    "input_admission_identity",
    "input_authorization_identity",
    "net_instance_identity",
    "occurrence_identity",
    "predecessor_marking_identity",
    "predecessor_revision",
    "request_identity",
    "reservation_identity",
    "selected_binding_evidence_identity",
}


class ExperimentalWorkflowPureActionReservationLifecycleState(StrEnum):
    RESERVED = "reserved"
    COMMITTED = "committed"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionReservationLifecycleIdentity:
    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or len(self.value) != 64:
            raise ValueError("lifecycle identity must be a SHA-256 digest")
        if self.value != self.value.lower() or any(
            character not in "0123456789abcdef" for character in self.value
        ):
            raise ValueError(
                "lifecycle identity must be a lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionReservationLifecycleEvent:
    identity: ExperimentalWorkflowPureActionReservationLifecycleIdentity = (
        field(init=False)
    )
    reservation: ExperimentalWorkflowPureActionReservation
    state: ExperimentalWorkflowPureActionReservationLifecycleState
    commit_identity: ExperimentalWorkflowPureActionCommitIdentity | None = None

    def __post_init__(self) -> None:
        if (
            type(self.reservation)
            is not ExperimentalWorkflowPureActionReservation
        ):
            raise TypeError(
                "reservation must be ExperimentalWorkflowPureActionReservation"
            )
        if (
            type(self.state)
            is not ExperimentalWorkflowPureActionReservationLifecycleState
        ):
            raise TypeError("state must be reservation lifecycle state")
        if (
            self.state
            is ExperimentalWorkflowPureActionReservationLifecycleState.RESERVED
        ):
            if self.commit_identity is not None:
                raise ValueError(
                    "reserved lifecycle event prohibits commit identity"
                )
        elif (
            type(self.commit_identity)
            is not ExperimentalWorkflowPureActionCommitIdentity
        ):
            raise TypeError(
                "committed lifecycle event requires commit identity"
            )
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionReservationLifecycleIdentity(
                stable_identity(
                    _DOMAIN,
                    self.reservation.identity.value,
                    self.state.value,
                    None
                    if self.commit_identity is None
                    else self.commit_identity.value,
                )
            ),
        )


@final
class ExperimentalWorkflowPureActionReservationLifecycleJsonCodec:
    """Strict canonical JSON codec for one identity-only lifecycle event."""

    __slots__ = ()

    def encode(
        self, event: ExperimentalWorkflowPureActionReservationLifecycleEvent
    ) -> bytes:
        if (
            type(event)
            is not ExperimentalWorkflowPureActionReservationLifecycleEvent
        ):
            raise TypeError("event must be reservation lifecycle event")
        reservation = event.reservation
        document = {
            "commit_identity": (
                None
                if event.commit_identity is None
                else event.commit_identity.value
            ),
            "identity": event.identity.value,
            "reservation": {
                "attempt_identity": reservation.attempt_identity.value,
                "attempt_ordinal": reservation.attempt_ordinal,
                "cpn_plan_identity": (
                    None
                    if reservation.cpn_plan_identity is None
                    else reservation.cpn_plan_identity.value
                ),
                "execution_bindings_identity": (
                    reservation.execution_bindings_identity.value
                ),
                "execution_plan_identity": (
                    reservation.execution_plan_identity.value
                ),
                "input_admission_identity": (
                    None
                    if reservation.input_admission_identity is None
                    else reservation.input_admission_identity.value
                ),
                "input_authorization_identity": (
                    None
                    if reservation.input_authorization_identity is None
                    else reservation.input_authorization_identity.value
                ),
                "net_instance_identity": (
                    reservation.net_instance_identity.value
                ),
                "occurrence_identity": reservation.occurrence_identity.value,
                "predecessor_marking_identity": (
                    reservation.predecessor_marking_identity.value
                ),
                "predecessor_revision": reservation.predecessor_revision,
                "request_identity": reservation.request_identity.value,
                "reservation_identity": reservation.identity.value,
                "selected_binding_evidence_identity": (
                    reservation.selected_binding_evidence_identity.value
                ),
            },
            "schema": _SCHEMA,
            "state": event.state.value,
        }
        encoded = json.dumps(
            document,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAX_BYTES:
            raise ValueError("lifecycle event exceeds canonical byte limit")
        return encoded

    def decode(
        self, value: bytes
    ) -> ExperimentalWorkflowPureActionReservationLifecycleEvent:
        if type(value) is not bytes or not value or len(value) > _MAX_BYTES:
            raise ValueError("lifecycle event must be bounded nonempty bytes")
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("lifecycle event is not canonical JSON") from error
        if type(document) is not dict or set(document) != {
            "commit_identity",
            "identity",
            "reservation",
            "schema",
            "state",
        }:
            raise ValueError("lifecycle event schema is closed")
        if document["schema"] != _SCHEMA:
            raise ValueError("lifecycle event schema is unsupported")
        raw = document["reservation"]
        if type(raw) is not dict or set(raw) != _RESERVATION_KEYS:
            raise ValueError("reservation lifecycle schema is closed")
        event = ExperimentalWorkflowPureActionReservationLifecycleEvent(
            reservation=_reservation_from_document(raw),
            state=ExperimentalWorkflowPureActionReservationLifecycleState(
                _text(document["state"], "state")
            ),
            commit_identity=(
                None
                if document["commit_identity"] is None
                else ExperimentalWorkflowPureActionCommitIdentity(
                    _text(document["commit_identity"], "commit_identity")
                )
            ),
        )
        if event.identity.value != _text(document["identity"], "identity"):
            raise ValueError("lifecycle event identity mismatch")
        if self.encode(event) != value:
            raise ValueError("lifecycle event bytes are not canonical")
        return event


class ExperimentalWorkflowPureActionReservationLifecycleReadStatus(StrEnum):
    FOUND = "found"
    LEGACY_PARTIAL = "legacy_partial"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionReservationLifecycleReadResult:
    status: ExperimentalWorkflowPureActionReservationLifecycleReadStatus
    events: tuple[ExperimentalWorkflowPureActionReservationLifecycleEvent, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionReservationLifecycleReadStatus
        ):
            raise TypeError("status must be lifecycle read status")
        if type(self.events) is not tuple or any(
            type(event)
            is not ExperimentalWorkflowPureActionReservationLifecycleEvent
            for event in self.events
        ):
            raise TypeError("events must contain lifecycle events")
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")
        found = (
            ExperimentalWorkflowPureActionReservationLifecycleReadStatus.FOUND
        )
        if self.status is found:
            if not self.events or self.diagnostics:
                raise ValueError(
                    "found lifecycle requires events without diagnostics"
                )
            lifecycle_state = (
                ExperimentalWorkflowPureActionReservationLifecycleState
            )
            if (
                len(self.events) > 2
                or self.events[0].state is not lifecycle_state.RESERVED
                or any(
                    event.reservation != self.events[0].reservation
                    for event in self.events
                )
                or (
                    len(self.events) == 2
                    and self.events[1].state is not lifecycle_state.COMMITTED
                )
            ):
                raise ValueError(
                    "found lifecycle events are not a valid sequence"
                )
        elif self.events or not self.diagnostics:
            raise ValueError(
                "non-found lifecycle requires diagnostics without events"
            )


class ExperimentalWorkflowPureActionReservationLifecycleRepository(ABC):
    @abstractmethod
    def load_reservation_lifecycle(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionReservationLifecycleReadResult:
        raise NotImplementedError


_LifecycleRepository = (
    ExperimentalWorkflowPureActionReservationLifecycleRepository
)


@final
class ExperimentalWorkflowPureActionReservationLifecycleReplayService:
    """Structurally replay one durable identity-only reservation lifecycle."""

    __slots__ = ("_repository",)

    def __init__(
        self,
        repository: _LifecycleRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionReservationLifecycleRepository,
        ):
            raise TypeError(
                "repository must implement the lifecycle repository"
            )
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "reservation lifecycle replay service is not subclassable"
        )

    def execute(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionReservationLifecycleReadResult:
        return self._repository.load_reservation_lifecycle(reservation_identity)


def _reservation_from_document(
    raw: dict[object, object],
) -> ExperimentalWorkflowPureActionReservation:
    optional_admission = raw["input_admission_identity"]
    optional_authorization = raw["input_authorization_identity"]
    optional_cpn = raw["cpn_plan_identity"]
    reservation = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=ExperimentalWorkflowPureActionExecutionPlanIdentity(
            _text(raw["execution_plan_identity"], "execution_plan_identity")
        ),
        execution_bindings_identity=ExperimentalWorkflowPureActionExecutionBindingsIdentity(
            _text(
                raw["execution_bindings_identity"],
                "execution_bindings_identity",
            )
        ),
        selected_binding_evidence_identity=ExperimentalWorkflowSelectedBindingEvidenceIdentity(
            _text(
                raw["selected_binding_evidence_identity"],
                "selected_binding_evidence_identity",
            )
        ),
        request_identity=WorkflowFiringRequestIdentity(
            _text(raw["request_identity"], "request_identity")
        ),
        net_instance_identity=WorkflowNetInstanceIdentity(
            _text(raw["net_instance_identity"], "net_instance_identity")
        ),
        predecessor_marking_identity=WorkflowMarkingIdentity(
            _text(
                raw["predecessor_marking_identity"],
                "predecessor_marking_identity",
            )
        ),
        predecessor_revision=_integer(
            raw["predecessor_revision"], "predecessor_revision"
        ),
        occurrence_identity=WorkflowOccurrenceIdentity(
            _text(raw["occurrence_identity"], "occurrence_identity")
        ),
        attempt_identity=WorkflowAttemptIdentity(
            _text(raw["attempt_identity"], "attempt_identity")
        ),
        attempt_ordinal=_integer(raw["attempt_ordinal"], "attempt_ordinal"),
        input_admission_identity=(
            None
            if optional_admission is None
            else ExperimentalWorkflowPureActionAdmittedInputsIdentity(
                _text(optional_admission, "input_admission_identity")
            )
        ),
        input_authorization_identity=(
            None
            if optional_authorization is None
            else ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                _text(optional_authorization, "input_authorization_identity")
            )
        ),
        cpn_plan_identity=(
            None
            if optional_cpn is None
            else ExperimentalWorkflowPureActionCpnPlanIdentity(
                _text(optional_cpn, "cpn_plan_identity")
            )
        ),
    )
    if reservation.identity.value != _text(
        raw["reservation_identity"], "reservation_identity"
    ):
        raise ValueError("reservation lifecycle identity mismatch")
    return reservation


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise ValueError(f"{label} must be nonempty text")
    return value


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


__all__ = [
    "ExperimentalWorkflowPureActionReservationLifecycleEvent",
    "ExperimentalWorkflowPureActionReservationLifecycleIdentity",
    "ExperimentalWorkflowPureActionReservationLifecycleJsonCodec",
    "ExperimentalWorkflowPureActionReservationLifecycleReadResult",
    "ExperimentalWorkflowPureActionReservationLifecycleReadStatus",
    "ExperimentalWorkflowPureActionReservationLifecycleReplayService",
    "ExperimentalWorkflowPureActionReservationLifecycleRepository",
    "ExperimentalWorkflowPureActionReservationLifecycleState",
]
