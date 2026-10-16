"""Records and nominal repository for pure-action reservations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from projectkoios.workflow.actions import (
    ExperimentalWorkflowSelectedBindingEvidenceIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
    ExperimentalWorkflowPureActionExecutionBindingsIdentity,
    ExperimentalWorkflowPureActionExecutionPlanIdentity,
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
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceAuthority,
)
from .pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
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
    net_instance_identity: WorkflowNetInstanceIdentity
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
                self.net_instance_identity,
                WorkflowNetInstanceIdentity,
                "net_instance_identity",
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
        if (
            type(self.source_authorities) is not tuple
            or len(self.source_authorities) > 1_024
            or any(
                type(item)
                is not ExperimentalWorkflowPureActionInputSourceAuthority
                for item in self.source_authorities
            )
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


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommittedSnapshot:
    """One atomically observed compact commit, coordinates, and event bytes."""

    coordinates: ExperimentalWorkflowPureActionCommitCoordinates
    record: ExperimentalWorkflowPureActionCommitRecord
    event_bytes: bytes = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.coordinates) is not (
            ExperimentalWorkflowPureActionCommitCoordinates
        ):
            raise TypeError(
                "coordinates must be "
                "ExperimentalWorkflowPureActionCommitCoordinates"
            )
        if type(self.record) is not ExperimentalWorkflowPureActionCommitRecord:
            raise TypeError(
                "record must be ExperimentalWorkflowPureActionCommitRecord"
            )
        if type(self.event_bytes) is not bytes or not self.event_bytes:
            raise TypeError("event_bytes must be nonempty bytes")
        if (
            self.record.commit_identity != self.coordinates.commit_identity
            or self.record.reservation_identity
            != self.coordinates.reservation_identity
            or self.record.net_instance_identity
            != self.coordinates.net_instance_identity
            or self.record.predecessor_marking_identity
            != self.coordinates.predecessor_marking_identity
            or self.record.predecessor_revision
            != self.coordinates.predecessor_revision
            or self.record.successor_marking_identity
            != self.coordinates.successor_marking_identity
            or self.record.successor_revision
            != self.coordinates.successor_revision
        ):
            raise ValueError(
                "committed snapshot coordinates differ from record"
            )


class ExperimentalWorkflowPureActionCommitReadStatus(StrEnum):
    """Closed result of atomically reading one retained compact commit."""

    FOUND = "found"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommitReadResult:
    """Expose one compact committed snapshot only after exact validation."""

    status: ExperimentalWorkflowPureActionCommitReadStatus
    snapshot: ExperimentalWorkflowPureActionCommittedSnapshot | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionCommitReadStatus
        ):
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionCommitReadStatus"
            )
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")
        if self.status is ExperimentalWorkflowPureActionCommitReadStatus.FOUND:
            if type(self.snapshot) is not (
                ExperimentalWorkflowPureActionCommittedSnapshot
            ):
                raise TypeError("found status requires committed snapshot")
            if self.diagnostics:
                raise ValueError("found status prohibits diagnostics")
        elif self.snapshot is not None:
            raise ValueError("non-found status prohibits committed snapshot")
        elif not self.diagnostics:
            raise ValueError("non-found status requires diagnostics")


class ExperimentalWorkflowPureActionCommitStatus(StrEnum):
    """Closed atomic commit result for one reserved predecessor."""

    COMMITTED = "committed"
    IDEMPOTENT = "idempotent"
    STALE = "stale"
    CONFLICT = "conflict"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


__all__ = [
    "ExperimentalWorkflowPureActionCommitCoordinates",
    "ExperimentalWorkflowPureActionCommitIdentity",
    "ExperimentalWorkflowPureActionCommitReadResult",
    "ExperimentalWorkflowPureActionCommitReadStatus",
    "ExperimentalWorkflowPureActionCommitRecord",
    "ExperimentalWorkflowPureActionCommitStatus",
    "ExperimentalWorkflowPureActionCommittedSnapshot",
    "ExperimentalWorkflowPureActionCurrentPredecessor",
    "ExperimentalWorkflowPureActionReservation",
    "ExperimentalWorkflowPureActionReservationIdentity",
    "ExperimentalWorkflowPureActionReservationResult",
    "ExperimentalWorkflowPureActionReserveStatus",
    "ExperimentalWorkflowPureActionRevalidationStatus",
]
