"""Experimental current-predecessor reservation for one pure external action."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from threading import Lock
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowFiringRequestCoordinates,
    ExperimentalWorkflowFiringRequestFactory,
    ExperimentalWorkflowSelectedBindingEvidence,
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow_sdk.firing import WorkflowFiringRequest
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)
from projectkoios.workflow_sdk.payloads import WorkflowInlinePayload

_RESERVATION_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-reservation:1"
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionReservationIdentity:
    """Content identity of one exact predecessor reservation."""

    value: str

    def __post_init__(self) -> None:
        if (
            type(self.value) is not str
            or len(self.value) != 64
            or self.value != self.value.lower()
            or any(
                character not in "0123456789abcdef" for character in self.value
            )
        ):
            raise ValueError(
                "pure action reservation identity must be 64 lowercase hex"
            )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCurrentPredecessor:
    """One repository-owned current net-instance coordinate."""

    net_instance_identity: WorkflowNetInstanceIdentity
    marking_identity: WorkflowMarkingIdentity
    revision: int

    def __post_init__(self) -> None:
        if type(self.net_instance_identity) is not WorkflowNetInstanceIdentity:
            raise TypeError(
                "net_instance_identity must be WorkflowNetInstanceIdentity"
            )
        if type(self.marking_identity) is not WorkflowMarkingIdentity:
            raise TypeError("marking_identity must be WorkflowMarkingIdentity")
        if type(self.revision) is not int:
            raise TypeError("revision must be an integer")
        if self.revision < 0:
            raise ValueError("revision must be nonnegative")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionReservation:
    """Bind one plan-selected request to an exact predecessor coordinate."""

    identity: ExperimentalWorkflowPureActionReservationIdentity = field(
        init=False
    )
    execution_plan_identity: ExperimentalWorkflowPureActionExecutionPlanIdentity
    execution_bindings_identity: (
        ExperimentalWorkflowPureActionExecutionBindingsIdentity
    )
    selected_binding_evidence_identity: (
        ExperimentalWorkflowSelectedBindingEvidenceIdentity
    )
    request_identity: WorkflowFiringRequestIdentity
    net_instance_identity: WorkflowNetInstanceIdentity
    predecessor_marking_identity: WorkflowMarkingIdentity
    predecessor_revision: int
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    attempt_ordinal: int

    def __post_init__(self) -> None:
        expected = (
            (
                "execution_plan_identity",
                self.execution_plan_identity,
                ExperimentalWorkflowPureActionExecutionPlanIdentity,
            ),
            (
                "execution_bindings_identity",
                self.execution_bindings_identity,
                ExperimentalWorkflowPureActionExecutionBindingsIdentity,
            ),
            (
                "selected_binding_evidence_identity",
                self.selected_binding_evidence_identity,
                ExperimentalWorkflowSelectedBindingEvidenceIdentity,
            ),
            (
                "request_identity",
                self.request_identity,
                WorkflowFiringRequestIdentity,
            ),
            (
                "net_instance_identity",
                self.net_instance_identity,
                WorkflowNetInstanceIdentity,
            ),
            (
                "predecessor_marking_identity",
                self.predecessor_marking_identity,
                WorkflowMarkingIdentity,
            ),
            (
                "occurrence_identity",
                self.occurrence_identity,
                WorkflowOccurrenceIdentity,
            ),
            (
                "attempt_identity",
                self.attempt_identity,
                WorkflowAttemptIdentity,
            ),
        )
        for name, value, nominal_type in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        for name in ("predecessor_revision", "attempt_ordinal"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionReservationIdentity(
                stable_identity(
                    _RESERVATION_IDENTITY_DOMAIN,
                    self.execution_plan_identity.value,
                    self.execution_bindings_identity.value,
                    self.selected_binding_evidence_identity.value,
                    self.request_identity.value,
                    self.net_instance_identity.value,
                    self.predecessor_marking_identity.value,
                    self.predecessor_revision,
                    self.occurrence_identity.value,
                    self.attempt_identity.value,
                    self.attempt_ordinal,
                )
            ),
        )


class ExperimentalWorkflowPureActionReserveStatus(StrEnum):
    """Closed result of attempting to reserve one current predecessor."""

    RESERVED = "reserved"
    IDEMPOTENT = "idempotent"
    STALE = "stale"
    CONFLICT = "conflict"


class ExperimentalWorkflowPureActionRevalidationStatus(StrEnum):
    """Closed current-state result for one retained reservation."""

    CURRENT = "current"
    ABSENT = "absent"
    STALE = "stale"
    CONSUMED = "consumed"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionReservationResult:
    """Return a request only when its predecessor reservation succeeded."""

    status: ExperimentalWorkflowPureActionReserveStatus
    reservation: ExperimentalWorkflowPureActionReservation | None
    request: WorkflowFiringRequest | None

    def __post_init__(self) -> None:
        if type(self.status) is not ExperimentalWorkflowPureActionReserveStatus:
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionReserveStatus"
            )
        successful = self.status in {
            ExperimentalWorkflowPureActionReserveStatus.RESERVED,
            ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT,
        }
        if successful:
            if type(self.reservation) is not (
                ExperimentalWorkflowPureActionReservation
            ):
                raise TypeError("successful reservation requires reservation")
            if type(self.request) is not WorkflowFiringRequest:
                raise TypeError("successful reservation requires request")
            if self.reservation.request_identity != self.request.identity:
                raise ValueError(
                    "reservation request identity differs from request"
                )
        elif self.reservation is not None or self.request is not None:
            raise ValueError("failed reservation must not expose request state")


class ExperimentalWorkflowPureActionReservationRepository(ABC):
    """Nominal atomic boundary for current predecessor reservations."""

    __slots__ = ()

    @abstractmethod
    def reserve(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionReserveStatus:
        """Atomically reserve the exact current predecessor or fail closed."""

    @abstractmethod
    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        """Return whether the exact retained reservation remains current."""


@final
class ExperimentalInMemoryPureActionReservationRepository(
    ExperimentalWorkflowPureActionReservationRepository
):
    """Thread-safe non-durable reference used as software evidence."""

    __slots__ = ("_active", "_consumed", "_current", "_lock")

    def __init__(
        self,
        predecessors: tuple[
            ExperimentalWorkflowPureActionCurrentPredecessor, ...
        ],
        *,
        consumed_reservation_identities: tuple[
            ExperimentalWorkflowPureActionReservationIdentity, ...
        ] = (),
    ) -> None:
        if type(predecessors) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCurrentPredecessor
            for item in predecessors
        ):
            raise TypeError(
                "predecessors must contain current predecessor records"
            )
        if type(consumed_reservation_identities) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionReservationIdentity
            for item in consumed_reservation_identities
        ):
            raise TypeError(
                "consumed_reservation_identities must contain reservation "
                "identities"
            )
        identities = tuple(item.net_instance_identity for item in predecessors)
        if len(identities) != len(set(identities)):
            raise ValueError("current predecessor net instances must be unique")
        if len(consumed_reservation_identities) != len(
            set(consumed_reservation_identities)
        ):
            raise ValueError("consumed reservation identities must be unique")
        self._current = {
            item.net_instance_identity: item for item in predecessors
        }
        self._active: dict[
            WorkflowNetInstanceIdentity,
            ExperimentalWorkflowPureActionReservation,
        ] = {}
        self._consumed = set(consumed_reservation_identities)
        self._lock = Lock()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalInMemoryPureActionReservationRepository "
            "is not subclassable"
        )

    def reserve(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionReserveStatus:
        validated = _reconstruct_reservation(reservation)
        with self._lock:
            if not self._matches_current(validated):
                return ExperimentalWorkflowPureActionReserveStatus.STALE
            existing = self._active.get(validated.net_instance_identity)
            if existing is not None:
                if existing == validated:
                    return (
                        ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT
                    )
                return ExperimentalWorkflowPureActionReserveStatus.CONFLICT
            if validated.identity in self._consumed:
                return ExperimentalWorkflowPureActionReserveStatus.CONFLICT
            self._active[validated.net_instance_identity] = validated
            return ExperimentalWorkflowPureActionReserveStatus.RESERVED

    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        validated = _reconstruct_reservation(reservation)
        with self._lock:
            if validated.identity in self._consumed:
                return ExperimentalWorkflowPureActionRevalidationStatus.CONSUMED
            if self._active.get(validated.net_instance_identity) != validated:
                return ExperimentalWorkflowPureActionRevalidationStatus.ABSENT
            if not self._matches_current(validated):
                return ExperimentalWorkflowPureActionRevalidationStatus.STALE
            return ExperimentalWorkflowPureActionRevalidationStatus.CURRENT

    def advance_current_predecessor(
        self,
        predecessor: ExperimentalWorkflowPureActionCurrentPredecessor,
    ) -> None:
        """Advance one current coordinate without permitting revision rewind."""
        if (
            type(predecessor)
            is not ExperimentalWorkflowPureActionCurrentPredecessor
        ):
            raise TypeError(
                "predecessor must be "
                "ExperimentalWorkflowPureActionCurrentPredecessor"
            )
        with self._lock:
            current = self._current.get(predecessor.net_instance_identity)
            if current is not None and predecessor.revision <= current.revision:
                raise ValueError("current predecessor revision must advance")
            self._current[predecessor.net_instance_identity] = predecessor

    def _matches_current(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> bool:
        current = self._current.get(reservation.net_instance_identity)
        return current == ExperimentalWorkflowPureActionCurrentPredecessor(
            net_instance_identity=reservation.net_instance_identity,
            marking_identity=reservation.predecessor_marking_identity,
            revision=reservation.predecessor_revision,
        )


@final
class ExperimentalWorkflowPureActionReservationService:
    """Construct an exact SDK request and reserve its current predecessor."""

    __slots__ = ("_repository",)

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionReservationRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionReservationRepository,
        ):
            raise TypeError(
                "repository must implement "
                "ExperimentalWorkflowPureActionReservationRepository"
            )
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionReservationService "
            "is not subclassable"
        )

    def reserve(
        self,
        *,
        execution_bindings: ExperimentalWorkflowPureActionExecutionBindings,
        selected_binding_evidence: ExperimentalWorkflowSelectedBindingEvidence,
        coordinates: ExperimentalWorkflowFiringRequestCoordinates,
        inputs: tuple[WorkflowInlinePayload, ...],
    ) -> ExperimentalWorkflowPureActionReservationResult:
        """Build the plan-selected request and reserve its predecessor."""
        if type(execution_bindings) is not (
            ExperimentalWorkflowPureActionExecutionBindings
        ):
            raise TypeError(
                "execution_bindings must be "
                "ExperimentalWorkflowPureActionExecutionBindings"
            )
        bindings = ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=execution_bindings.execution_plan,
            integration_manifest=execution_bindings.integration_manifest,
        )
        if bindings != execution_bindings:
            raise ValueError("execution bindings differ after validation")
        if type(selected_binding_evidence) is not (
            ExperimentalWorkflowSelectedBindingEvidence
        ):
            raise TypeError(
                "selected_binding_evidence must be "
                "ExperimentalWorkflowSelectedBindingEvidence"
            )
        if (
            selected_binding_evidence.profile_identity
            != bindings.execution_plan.selected_binding_profile_identity
        ):
            raise ValueError("selected-binding profile differs from the plan")
        mapping = bindings.execution_plan.output_mapping_descriptor
        request = ExperimentalWorkflowFiringRequestFactory().execute(
            transition_binding=mapping.transition_binding,
            firer_descriptor=mapping.firer_descriptor,
            selected_binding_evidence=selected_binding_evidence,
            coordinates=coordinates,
            inputs=inputs,
        )
        context = request.context
        reservation = ExperimentalWorkflowPureActionReservation(
            execution_plan_identity=bindings.execution_plan.identity,
            execution_bindings_identity=bindings.identity,
            selected_binding_evidence_identity=selected_binding_evidence.identity,
            request_identity=request.identity,
            net_instance_identity=context.net_instance_identity,
            predecessor_marking_identity=context.predecessor_marking_identity,
            predecessor_revision=context.predecessor_revision,
            occurrence_identity=context.occurrence_identity,
            attempt_identity=context.attempt_identity,
            attempt_ordinal=context.attempt_ordinal,
        )
        status = self._repository.reserve(reservation)
        if status in {
            ExperimentalWorkflowPureActionReserveStatus.RESERVED,
            ExperimentalWorkflowPureActionReserveStatus.IDEMPOTENT,
        }:
            return ExperimentalWorkflowPureActionReservationResult(
                status=status,
                reservation=reservation,
                request=request,
            )
        return ExperimentalWorkflowPureActionReservationResult(
            status=status,
            reservation=None,
            request=None,
        )

    def revalidate(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
    ) -> ExperimentalWorkflowPureActionRevalidationStatus:
        """Revalidate one exact reservation after owner execution."""
        return self._repository.revalidate(reservation)


def _reconstruct_reservation(
    value: ExperimentalWorkflowPureActionReservation,
) -> ExperimentalWorkflowPureActionReservation:
    if type(value) is not ExperimentalWorkflowPureActionReservation:
        raise TypeError(
            "reservation must be ExperimentalWorkflowPureActionReservation"
        )
    validated = ExperimentalWorkflowPureActionReservation(
        execution_plan_identity=value.execution_plan_identity,
        execution_bindings_identity=value.execution_bindings_identity,
        selected_binding_evidence_identity=(
            value.selected_binding_evidence_identity
        ),
        request_identity=value.request_identity,
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        occurrence_identity=value.occurrence_identity,
        attempt_identity=value.attempt_identity,
        attempt_ordinal=value.attempt_ordinal,
    )
    if validated != value:
        raise ValueError("reservation differs after validation")
    return validated


__all__ = [
    "ExperimentalInMemoryPureActionReservationRepository",
    "ExperimentalWorkflowPureActionCurrentPredecessor",
    "ExperimentalWorkflowPureActionReservation",
    "ExperimentalWorkflowPureActionReservationIdentity",
    "ExperimentalWorkflowPureActionReservationRepository",
    "ExperimentalWorkflowPureActionReservationResult",
    "ExperimentalWorkflowPureActionReservationService",
    "ExperimentalWorkflowPureActionReserveStatus",
    "ExperimentalWorkflowPureActionRevalidationStatus",
]
