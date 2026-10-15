"""Experimental current-predecessor reservation for one pure external action."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from threading import Lock
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlan,
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow_sdk.firing import WorkflowFiringRequest
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)

from .pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceAuthority,
)
from .pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
)
from .pure_action_source_repository import (
    ExperimentalWorkflowPureActionInputSourceLoadResult,
    ExperimentalWorkflowPureActionInputSourceLoadStatus,
    ExperimentalWorkflowPureActionInputSourceReference,
    ExperimentalWorkflowPureActionInputSourceRepository,
)

_LEGACY_RESERVATION_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-reservation:1"
)
_LEGACY_RESERVATION_WITH_INPUTS_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-reservation:2"
)
_RESERVATION_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-reservation:0"
)
_CPN_PLAN_RESERVATION_IDENTITY_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-cpn-reservation:0"
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
    input_admission_identity: (
        ExperimentalWorkflowPureActionAdmittedInputsIdentity | None
    ) = None
    input_authorization_identity: (
        ExperimentalWorkflowPureActionAuthorizedInputsIdentity | None
    ) = None
    cpn_plan_identity: ExperimentalWorkflowPureActionCpnPlanIdentity | None = (
        None
    )

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
        if (
            self.input_admission_identity is not None
            and type(self.input_admission_identity)
            is not ExperimentalWorkflowPureActionAdmittedInputsIdentity
        ):
            raise TypeError(
                "input_admission_identity must be "
                "ExperimentalWorkflowPureActionAdmittedInputsIdentity or None"
            )
        if (
            self.input_authorization_identity is not None
            and type(self.input_authorization_identity)
            is not ExperimentalWorkflowPureActionAuthorizedInputsIdentity
        ):
            raise TypeError(
                "input_authorization_identity must be "
                "ExperimentalWorkflowPureActionAuthorizedInputsIdentity or None"
            )
        if (
            self.input_authorization_identity is not None
            and self.input_admission_identity is None
        ):
            raise ValueError("input authorization requires input admission")
        if (
            self.cpn_plan_identity is not None
            and type(self.cpn_plan_identity)
            is not ExperimentalWorkflowPureActionCpnPlanIdentity
        ):
            raise TypeError(
                "cpn_plan_identity must be "
                "ExperimentalWorkflowPureActionCpnPlanIdentity or None"
            )
        if (
            self.cpn_plan_identity is not None
            and self.input_authorization_identity is None
        ):
            raise ValueError(
                "CPN plan reservation requires input authorization"
            )
        parts: tuple[object, ...] = (
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
        domain = _LEGACY_RESERVATION_IDENTITY_DOMAIN
        if self.input_admission_identity is not None:
            domain = _LEGACY_RESERVATION_WITH_INPUTS_IDENTITY_DOMAIN
            parts += (self.input_admission_identity.value,)
        if self.input_authorization_identity is not None:
            domain = _RESERVATION_IDENTITY_DOMAIN
            parts += (self.input_authorization_identity.value,)
        if self.cpn_plan_identity is not None:
            domain = _CPN_PLAN_RESERVATION_IDENTITY_DOMAIN
            parts += (self.cpn_plan_identity.value,)
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionReservationIdentity(
                stable_identity(domain, *parts)
            ),
        )


class ExperimentalWorkflowPureActionReserveStatus(StrEnum):
    """Closed result of attempting to reserve one current predecessor."""

    RESERVED = "reserved"
    IDEMPOTENT = "idempotent"
    STALE = "stale"
    CONFLICT = "conflict"
    SOURCE_ABSENT = "source_absent"
    SOURCE_INCOMPATIBLE = "source_incompatible"
    SOURCE_CORRUPT = "source_corrupt"
    SOURCE_INDETERMINATE = "source_indeterminate"
    SOURCE_ERROR = "source_error"
    SOURCE_CONFLICT = "source_conflict"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


class ExperimentalWorkflowPureActionRevalidationStatus(StrEnum):
    """Closed current-state result for one retained reservation."""

    CURRENT = "current"
    ABSENT = "absent"
    STALE = "stale"
    CONSUMED = "consumed"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


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


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommitIdentity:
    """Content identity retained by the atomic reservation commit boundary."""

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
            raise ValueError("commit identity must be 64 lowercase hex")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommitCoordinates:
    """Compact marking coordinates atomically retained with one commit."""

    commit_identity: ExperimentalWorkflowPureActionCommitIdentity
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity
    net_instance_identity: WorkflowNetInstanceIdentity
    predecessor_marking_identity: WorkflowMarkingIdentity
    predecessor_revision: int
    successor_marking_identity: WorkflowMarkingIdentity
    successor_revision: int

    def __post_init__(self) -> None:
        expected = (
            (
                self.commit_identity,
                ExperimentalWorkflowPureActionCommitIdentity,
                "commit_identity",
            ),
            (
                self.reservation_identity,
                ExperimentalWorkflowPureActionReservationIdentity,
                "reservation_identity",
            ),
            (
                self.net_instance_identity,
                WorkflowNetInstanceIdentity,
                "net_instance_identity",
            ),
            (
                self.predecessor_marking_identity,
                WorkflowMarkingIdentity,
                "predecessor_marking_identity",
            ),
            (
                self.successor_marking_identity,
                WorkflowMarkingIdentity,
                "successor_marking_identity",
            ),
        )
        for value, nominal_type, label in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{label} must be {nominal_type.__name__}")
        for label in ("predecessor_revision", "successor_revision"):
            value = getattr(self, label)
            if type(value) is not int:
                raise TypeError(f"{label} must be an integer")
            if value < 0:
                raise ValueError(f"{label} must be nonnegative")
        if self.successor_revision != self.predecessor_revision + 1:
            raise ValueError(
                "successor revision must immediately follow predecessor"
            )
        if self.successor_marking_identity == self.predecessor_marking_identity:
            raise ValueError("successor marking must differ from predecessor")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommitRecord:
    """Complete compact commit and admitted source-reference evidence."""

    commit_identity: ExperimentalWorkflowPureActionCommitIdentity
    cpn_plan_identity: ExperimentalWorkflowPureActionCpnPlanIdentity
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity
    input_authorization_identity: (
        ExperimentalWorkflowPureActionAuthorizedInputsIdentity
    )
    source_authorities: tuple[
        ExperimentalWorkflowPureActionInputSourceAuthority, ...
    ]
    invocation_outcome_identity: str
    request_identity: WorkflowFiringRequestIdentity
    owner_result_identity: WorkflowFiringResultIdentity
    mapped_result_identity: str
    firing_outcome_identity: str
    cpn_firing_result_identity: str
    predecessor_marking_identity: WorkflowMarkingIdentity
    predecessor_revision: int
    successor_marking_identity: WorkflowMarkingIdentity
    successor_revision: int

    def __post_init__(self) -> None:
        expected = (
            (
                self.commit_identity,
                ExperimentalWorkflowPureActionCommitIdentity,
                "commit_identity",
            ),
            (
                self.cpn_plan_identity,
                ExperimentalWorkflowPureActionCpnPlanIdentity,
                "cpn_plan_identity",
            ),
            (
                self.reservation_identity,
                ExperimentalWorkflowPureActionReservationIdentity,
                "reservation_identity",
            ),
            (
                self.input_authorization_identity,
                ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
                "input_authorization_identity",
            ),
            (
                self.request_identity,
                WorkflowFiringRequestIdentity,
                "request_identity",
            ),
            (
                self.owner_result_identity,
                WorkflowFiringResultIdentity,
                "owner_result_identity",
            ),
            (
                self.predecessor_marking_identity,
                WorkflowMarkingIdentity,
                "predecessor_marking_identity",
            ),
            (
                self.successor_marking_identity,
                WorkflowMarkingIdentity,
                "successor_marking_identity",
            ),
        )
        for value, nominal_type, label in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{label} must be {nominal_type.__name__}")
        if type(self.source_authorities) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionInputSourceAuthority
            for item in self.source_authorities
        ):
            raise TypeError(
                "source_authorities must contain "
                "ExperimentalWorkflowPureActionInputSourceAuthority"
            )
        authority_identities = tuple(
            item.identity for item in self.source_authorities
        )
        if len(authority_identities) != len(set(authority_identities)):
            raise ValueError("source authority identities must be unique")
        for label in (
            "invocation_outcome_identity",
            "mapped_result_identity",
            "firing_outcome_identity",
            "cpn_firing_result_identity",
        ):
            _validate_sha256(getattr(self, label), label)
        for label in ("predecessor_revision", "successor_revision"):
            value = getattr(self, label)
            if type(value) is not int:
                raise TypeError(f"{label} must be an integer")
            if value < 0:
                raise ValueError(f"{label} must be nonnegative")
        if self.successor_revision != self.predecessor_revision + 1:
            raise ValueError(
                "successor revision must immediately follow predecessor"
            )
        if self.successor_marking_identity == self.predecessor_marking_identity:
            raise ValueError("successor marking must differ from predecessor")


class ExperimentalWorkflowPureActionCommitStatus(StrEnum):
    """Closed atomic commit result for one reserved predecessor."""

    COMMITTED = "committed"
    IDEMPOTENT = "idempotent"
    STALE = "stale"
    CONFLICT = "conflict"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


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

    @abstractmethod
    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically retain a commit, consume, and advance the predecessor."""

    @abstractmethod
    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load compact committed coordinates for exact replay inspection."""

    @abstractmethod
    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the complete compact commit record for replay inspection."""

    @abstractmethod
    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the repository-owned current predecessor coordinate."""


@final
class ExperimentalInMemoryPureActionReservationRepository(
    ExperimentalWorkflowPureActionReservationRepository
):
    """Thread-safe non-durable reference used as software evidence."""

    __slots__ = (
        "_active",
        "_commit_records",
        "_commits",
        "_consumed",
        "_current",
        "_lock",
    )

    def __init__(
        self,
        predecessors: tuple[
            ExperimentalWorkflowPureActionCurrentPredecessor, ...
        ],
        *,
        consumed_reservation_identities: tuple[
            ExperimentalWorkflowPureActionReservationIdentity, ...
        ] = (),
        committed_coordinates: tuple[
            ExperimentalWorkflowPureActionCommitCoordinates, ...
        ] = (),
        committed_records: tuple[
            ExperimentalWorkflowPureActionCommitRecord, ...
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
        if type(committed_coordinates) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCommitCoordinates
            for item in committed_coordinates
        ):
            raise TypeError(
                "committed_coordinates must contain "
                "ExperimentalWorkflowPureActionCommitCoordinates"
            )
        if type(committed_records) is not tuple or any(
            type(item) is not ExperimentalWorkflowPureActionCommitRecord
            for item in committed_records
        ):
            raise TypeError(
                "committed_records must contain "
                "ExperimentalWorkflowPureActionCommitRecord"
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
        commit_reservations = tuple(
            item.reservation_identity for item in committed_coordinates
        )
        commit_identities = tuple(
            item.commit_identity for item in committed_coordinates
        )
        if len(commit_reservations) != len(set(commit_reservations)):
            raise ValueError("committed reservation identities must be unique")
        if len(commit_identities) != len(set(commit_identities)):
            raise ValueError("commit identities must be unique")
        self._commits = {
            item.reservation_identity: item for item in committed_coordinates
        }
        record_reservations = tuple(
            item.reservation_identity for item in committed_records
        )
        if len(record_reservations) != len(set(record_reservations)):
            raise ValueError(
                "commit record reservation identities must be unique"
            )
        self._commit_records = {
            item.reservation_identity: item for item in committed_records
        }
        for reservation_identity, record in self._commit_records.items():
            coordinates = self._commits.get(reservation_identity)
            if coordinates is None or not _record_matches_coordinates(
                record, coordinates
            ):
                raise ValueError(
                    "commit records must exactly match committed coordinates"
                )
        self._consumed = set(consumed_reservation_identities) | set(
            commit_reservations
        )
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

    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically retain compact commit state and advance the marking."""
        validated_reservation = _reconstruct_reservation(reservation)
        validated_coordinates = _reconstruct_commit_coordinates(coordinates)
        validated_record = (
            None if record is None else _reconstruct_commit_record(record)
        )
        if (
            validated_coordinates.reservation_identity
            != validated_reservation.identity
            or validated_coordinates.net_instance_identity
            != validated_reservation.net_instance_identity
            or validated_coordinates.predecessor_marking_identity
            != validated_reservation.predecessor_marking_identity
            or validated_coordinates.predecessor_revision
            != validated_reservation.predecessor_revision
        ):
            raise ValueError("commit coordinates differ from reservation")
        if validated_record is not None and (
            validated_record.reservation_identity
            != validated_reservation.identity
            or not _record_matches_coordinates(
                validated_record, validated_coordinates
            )
        ):
            raise ValueError("commit record differs from commit coordinates")
        with self._lock:
            existing = self._commits.get(validated_reservation.identity)
            if existing is not None:
                existing_record = self._commit_records.get(
                    validated_reservation.identity
                )
                if existing == validated_coordinates and (
                    validated_record is None
                    or existing_record == validated_record
                ):
                    return ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            if any(
                item.commit_identity == validated_coordinates.commit_identity
                for item in self._commits.values()
            ):
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            if not self._matches_current(validated_reservation):
                return ExperimentalWorkflowPureActionCommitStatus.STALE
            if (
                self._active.get(validated_reservation.net_instance_identity)
                != validated_reservation
                or validated_reservation.identity in self._consumed
            ):
                return ExperimentalWorkflowPureActionCommitStatus.CONFLICT
            active = dict(self._active)
            current = dict(self._current)
            consumed = set(self._consumed)
            commits = dict(self._commits)
            commit_records = dict(self._commit_records)
            del active[validated_reservation.net_instance_identity]
            consumed.add(validated_reservation.identity)
            commits[validated_reservation.identity] = validated_coordinates
            if validated_record is not None:
                commit_records[validated_reservation.identity] = (
                    validated_record
                )
            current[validated_reservation.net_instance_identity] = (
                ExperimentalWorkflowPureActionCurrentPredecessor(
                    net_instance_identity=(
                        validated_reservation.net_instance_identity
                    ),
                    marking_identity=(
                        validated_coordinates.successor_marking_identity
                    ),
                    revision=validated_coordinates.successor_revision,
                )
            )
            active, current, consumed, commits = _finalize_commit_state(
                active,
                current,
                consumed,
                commits,
            )
            self._active = active
            self._current = current
            self._consumed = consumed
            self._commits = commits
            self._commit_records = commit_records
            return ExperimentalWorkflowPureActionCommitStatus.COMMITTED

    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load exact retained coordinates without exposing mutable state."""
        if type(reservation_identity) is not (
            ExperimentalWorkflowPureActionReservationIdentity
        ):
            raise TypeError(
                "reservation_identity must be "
                "ExperimentalWorkflowPureActionReservationIdentity"
            )
        with self._lock:
            return self._commits.get(reservation_identity)

    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the complete compact retained commit record."""
        if type(reservation_identity) is not (
            ExperimentalWorkflowPureActionReservationIdentity
        ):
            raise TypeError(
                "reservation_identity must be "
                "ExperimentalWorkflowPureActionReservationIdentity"
            )
        with self._lock:
            return self._commit_records.get(reservation_identity)

    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the current compact marking coordinate."""
        if type(net_instance_identity) is not WorkflowNetInstanceIdentity:
            raise TypeError(
                "net_instance_identity must be WorkflowNetInstanceIdentity"
            )
        with self._lock:
            return self._current.get(net_instance_identity)

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

    __slots__ = ("_repository", "_source_repository")

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionReservationRepository,
        source_repository: ExperimentalWorkflowPureActionInputSourceRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionReservationRepository,
        ):
            raise TypeError(
                "repository must implement "
                "ExperimentalWorkflowPureActionReservationRepository"
            )
        if not isinstance(
            source_repository,
            ExperimentalWorkflowPureActionInputSourceRepository,
        ):
            raise TypeError(
                "source_repository must implement "
                "ExperimentalWorkflowPureActionInputSourceRepository"
            )
        self._repository = repository
        self._source_repository = source_repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionReservationService "
            "is not subclassable"
        )

    def reserve(
        self,
        *,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
        cpn_plan: ExperimentalWorkflowPureActionCpnPlan | None = None,
    ) -> ExperimentalWorkflowPureActionReservationResult:
        """Reserve only a repository-authorized, plan-selected SDK request."""
        authorized = _reconstruct_authorized_inputs(authorized_inputs)
        admitted = authorized.admitted_inputs
        if cpn_plan is not None:
            if type(cpn_plan) is not ExperimentalWorkflowPureActionCpnPlan:
                raise TypeError(
                    "cpn_plan must be "
                    "ExperimentalWorkflowPureActionCpnPlan or None"
                )
            if (
                cpn_plan.input_plan_identity
                != admitted.input_bindings.input_plan.identity
            ):
                raise ValueError("CPN plan differs from admitted input plan")
            if (
                cpn_plan.execution_profile
                != experimental_shadow_cpn_execution_profile()
            ):
                raise ValueError("CPN execution profile is unsupported")
        source_status = self.revalidate_sources(authorized)
        if source_status is not None:
            return ExperimentalWorkflowPureActionReservationResult(
                status=source_status,
                reservation=None,
                request=None,
            )
        bindings = admitted.input_bindings.execution_bindings
        selected_binding_evidence = admitted.selected_binding_evidence
        request = admitted.request
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
            input_admission_identity=admitted.identity,
            input_authorization_identity=authorized.identity,
            cpn_plan_identity=None if cpn_plan is None else cpn_plan.identity,
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

    def commit(
        self,
        reservation: ExperimentalWorkflowPureActionReservation,
        coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
        record: ExperimentalWorkflowPureActionCommitRecord | None = None,
    ) -> ExperimentalWorkflowPureActionCommitStatus:
        """Atomically consume and advance through the repository boundary."""
        return self._repository.commit(reservation, coordinates, record)

    def load_commit(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitCoordinates | None:
        """Load compact retained commit coordinates."""
        return self._repository.load_commit(reservation_identity)

    def load_commit_record(
        self,
        reservation_identity: ExperimentalWorkflowPureActionReservationIdentity,
    ) -> ExperimentalWorkflowPureActionCommitRecord | None:
        """Load the complete compact retained commit record."""
        return self._repository.load_commit_record(reservation_identity)

    def current_predecessor(
        self,
        net_instance_identity: WorkflowNetInstanceIdentity,
    ) -> ExperimentalWorkflowPureActionCurrentPredecessor | None:
        """Load the repository-owned current predecessor coordinate."""
        return self._repository.current_predecessor(net_instance_identity)

    def revalidate_sources(
        self,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
    ) -> ExperimentalWorkflowPureActionReserveStatus | None:
        """Re-resolve sources without reserving the predecessor."""
        authorized = _reconstruct_authorized_inputs(authorized_inputs)
        admitted = authorized.admitted_inputs
        for source, authority in zip(
            admitted.source_evidence,
            authorized.source_authorities,
            strict=True,
        ):
            reference = ExperimentalWorkflowPureActionInputSourceReference(
                source_kind=source.source_kind,
                source_profile_identity=source.source_profile_identity,
                source_identity=source.source_identity,
            )
            try:
                loaded = self._source_repository.load(reference)
            except Exception:
                return ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
            if type(loaded) is not (
                ExperimentalWorkflowPureActionInputSourceLoadResult
            ):
                return ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
            if loaded.status is not (
                ExperimentalWorkflowPureActionInputSourceLoadStatus.LOADED
            ):
                return _source_reserve_failure(loaded.status)
            if (
                loaded.evidence != source
                or loaded.revision_identity != authority.revision_identity
                or loaded.reference.identity != authority.reference_identity
            ):
                return (
                    ExperimentalWorkflowPureActionReserveStatus.SOURCE_CONFLICT
                )
        return None


def _reconstruct_commit_coordinates(
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


def _reconstruct_commit_record(
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


def _record_matches_coordinates(
    record: ExperimentalWorkflowPureActionCommitRecord,
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates,
) -> bool:
    return (
        record.commit_identity == coordinates.commit_identity
        and record.reservation_identity == coordinates.reservation_identity
        and record.predecessor_marking_identity
        == coordinates.predecessor_marking_identity
        and record.predecessor_revision == coordinates.predecessor_revision
        and record.successor_marking_identity
        == coordinates.successor_marking_identity
        and record.successor_revision == coordinates.successor_revision
    )


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _finalize_commit_state(
    active: dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionReservation,
    ],
    current: dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionCurrentPredecessor,
    ],
    consumed: set[ExperimentalWorkflowPureActionReservationIdentity],
    commits: dict[
        ExperimentalWorkflowPureActionReservationIdentity,
        ExperimentalWorkflowPureActionCommitCoordinates,
    ],
) -> tuple[
    dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionReservation,
    ],
    dict[
        WorkflowNetInstanceIdentity,
        ExperimentalWorkflowPureActionCurrentPredecessor,
    ],
    set[ExperimentalWorkflowPureActionReservationIdentity],
    dict[
        ExperimentalWorkflowPureActionReservationIdentity,
        ExperimentalWorkflowPureActionCommitCoordinates,
    ],
]:
    """Return staged state; assignment by the caller is the commit point."""
    return active, current, consumed, commits


def _source_reserve_failure(
    status: ExperimentalWorkflowPureActionInputSourceLoadStatus,
) -> ExperimentalWorkflowPureActionReserveStatus:
    return {
        ExperimentalWorkflowPureActionInputSourceLoadStatus.ABSENT: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_ABSENT
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.INCOMPATIBLE: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_INCOMPATIBLE
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.CORRUPT: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_CORRUPT
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.INDETERMINATE: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_INDETERMINATE
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.ERROR: (
            ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
        ),
    }[status]


def _reconstruct_authorized_inputs(
    value: ExperimentalWorkflowPureActionAuthorizedInputs,
) -> ExperimentalWorkflowPureActionAuthorizedInputs:
    if type(value) is not ExperimentalWorkflowPureActionAuthorizedInputs:
        raise TypeError(
            "authorized_inputs must be "
            "ExperimentalWorkflowPureActionAuthorizedInputs"
        )
    reconstructed = ExperimentalWorkflowPureActionAuthorizedInputs(
        admitted_inputs=value.admitted_inputs,
        source_authorities=value.source_authorities,
    )
    if reconstructed != value:
        raise ValueError("authorized inputs differ after validation")
    return reconstructed


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
        input_admission_identity=value.input_admission_identity,
        input_authorization_identity=value.input_authorization_identity,
        cpn_plan_identity=value.cpn_plan_identity,
    )
    if validated != value:
        raise ValueError("reservation differs after validation")
    return validated


__all__ = [
    "ExperimentalInMemoryPureActionReservationRepository",
    "ExperimentalWorkflowPureActionCommitCoordinates",
    "ExperimentalWorkflowPureActionCommitIdentity",
    "ExperimentalWorkflowPureActionCommitRecord",
    "ExperimentalWorkflowPureActionCommitStatus",
    "ExperimentalWorkflowPureActionCurrentPredecessor",
    "ExperimentalWorkflowPureActionReservation",
    "ExperimentalWorkflowPureActionReservationIdentity",
    "ExperimentalWorkflowPureActionReservationRepository",
    "ExperimentalWorkflowPureActionReservationResult",
    "ExperimentalWorkflowPureActionReservationService",
    "ExperimentalWorkflowPureActionReserveStatus",
    "ExperimentalWorkflowPureActionRevalidationStatus",
]
