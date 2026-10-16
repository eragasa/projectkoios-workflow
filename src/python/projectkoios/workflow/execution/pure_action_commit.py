"""Compatibility compact-only commit for pure-action firing candidates.

New supported experimental writes use the durable CPN commit service so compact
state, replay evidence, lifecycle, reservation consumption, and marking advance
share one atomic boundary. This module retains compact record construction and
the legacy writer for compatibility and migration evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowMappedActionResultIdentity,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlan,
    ExperimentalWorkflowPureActionCpnPlanIdentity,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetFiringOutcomeKind,
    ColoredPetriNetFiringResultIdentity,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionCommitCoordinates,
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionInputSourceAuthorityIdentity,
    ExperimentalWorkflowPureActionReservation,
    ExperimentalWorkflowPureActionReservationIdentity,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReservationService,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
)

from ._validation import (
    reconstruct_authorized_inputs,
    reconstruct_cpn_plan,
    reconstruct_successful_reservation,
)
from .pure_action_firing import (
    ExperimentalWorkflowPureActionFiringOutcome,
    ExperimentalWorkflowPureActionFiringOutcomeIdentity,
    ExperimentalWorkflowPureActionFiringStatus,
    _reconstruct_firing_outcome,
)
from .pure_action_invocation import (
    ExperimentalWorkflowPureActionInvocationOutcome,
    ExperimentalWorkflowPureActionInvocationOutcomeIdentity,
    ExperimentalWorkflowPureActionInvocationStatus,
    _reconstruct_invocation_outcome,
)

_COMMIT_DOMAIN = "projectkoios.workflow.experimental-pure-action-commit:0"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommit:
    """Compact identity-only evidence for one atomic pure-action commit."""

    identity: ExperimentalWorkflowPureActionCommitIdentity = field(init=False)
    cpn_plan_identity: ExperimentalWorkflowPureActionCpnPlanIdentity
    reservation_identity: ExperimentalWorkflowPureActionReservationIdentity
    input_authorization_identity: (
        ExperimentalWorkflowPureActionAuthorizedInputsIdentity
    )
    source_authority_identities: tuple[
        ExperimentalWorkflowPureActionInputSourceAuthorityIdentity, ...
    ]
    invocation_outcome_identity: (
        ExperimentalWorkflowPureActionInvocationOutcomeIdentity
    )
    request_identity: WorkflowFiringRequestIdentity
    owner_result_identity: WorkflowFiringResultIdentity
    mapped_result_identity: ExperimentalWorkflowMappedActionResultIdentity
    firing_outcome_identity: ExperimentalWorkflowPureActionFiringOutcomeIdentity
    cpn_firing_result_identity: ColoredPetriNetFiringResultIdentity
    predecessor_marking_identity: WorkflowMarkingIdentity
    predecessor_revision: int
    successor_marking_identity: WorkflowMarkingIdentity
    successor_revision: int

    def __post_init__(self) -> None:
        expected = (
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
                self.invocation_outcome_identity,
                ExperimentalWorkflowPureActionInvocationOutcomeIdentity,
                "invocation_outcome_identity",
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
                self.mapped_result_identity,
                ExperimentalWorkflowMappedActionResultIdentity,
                "mapped_result_identity",
            ),
            (
                self.firing_outcome_identity,
                ExperimentalWorkflowPureActionFiringOutcomeIdentity,
                "firing_outcome_identity",
            ),
            (
                self.cpn_firing_result_identity,
                ColoredPetriNetFiringResultIdentity,
                "cpn_firing_result_identity",
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
        if type(self.source_authority_identities) is not tuple or any(
            type(item)
            is not ExperimentalWorkflowPureActionInputSourceAuthorityIdentity
            for item in self.source_authority_identities
        ):
            raise TypeError(
                "source_authority_identities must contain "
                "ExperimentalWorkflowPureActionInputSourceAuthorityIdentity"
            )
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
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionCommitIdentity(
                stable_identity(
                    _COMMIT_DOMAIN,
                    self.cpn_plan_identity.value,
                    self.reservation_identity.value,
                    self.input_authorization_identity.value,
                    tuple(
                        item.value for item in self.source_authority_identities
                    ),
                    self.invocation_outcome_identity.value,
                    self.request_identity.value,
                    self.owner_result_identity.value,
                    self.mapped_result_identity.value,
                    self.firing_outcome_identity.value,
                    self.cpn_firing_result_identity.value,
                    self.predecessor_marking_identity.value,
                    self.predecessor_revision,
                    self.successor_marking_identity.value,
                    self.successor_revision,
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCommitResult:
    """Closed result of attempting one atomic pure-action commit."""

    status: ExperimentalWorkflowPureActionCommitStatus
    commit: ExperimentalWorkflowPureActionCommit | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.status) is not ExperimentalWorkflowPureActionCommitStatus:
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionCommitStatus"
            )
        successful = self.status in {
            ExperimentalWorkflowPureActionCommitStatus.COMMITTED,
            ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT,
        }
        if successful:
            if type(self.commit) is not ExperimentalWorkflowPureActionCommit:
                raise TypeError("successful commit result requires commit")
            if self.diagnostics:
                raise ValueError(
                    "successful commit result prohibits diagnostics"
                )
        else:
            if self.commit is not None:
                raise ValueError("failed commit result prohibits commit")
            if not self.diagnostics:
                raise ValueError("failed commit result requires diagnostics")
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")


@dataclass(frozen=True, slots=True)
class _PreparedCommitCandidate:
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs
    reservation: ExperimentalWorkflowPureActionReservation
    plan: ExperimentalWorkflowPureActionCpnPlan
    invocation: ExperimentalWorkflowPureActionInvocationOutcome
    firing: ExperimentalWorkflowPureActionFiringOutcome
    commit: ExperimentalWorkflowPureActionCommit
    coordinates: ExperimentalWorkflowPureActionCommitCoordinates
    record: ExperimentalWorkflowPureActionCommitRecord


@final
class ExperimentalWorkflowPureActionCommitService:
    """Compatibility writer for a compact-only pure CPN commit.

    New supported orchestration must use
    ``ExperimentalWorkflowPureActionDurableCpnCommitService``. This service
    remains public only for legacy-history, migration, and compatibility
    evidence until the experimental surface retirement task determines its
    removal path.
    """

    __slots__ = ("_reservation_service",)

    def __init__(
        self,
        reservation_service: ExperimentalWorkflowPureActionReservationService,
    ) -> None:
        if type(reservation_service) is not (
            ExperimentalWorkflowPureActionReservationService
        ):
            raise TypeError(
                "reservation_service must be "
                "ExperimentalWorkflowPureActionReservationService"
            )
        self._reservation_service = reservation_service

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCommitService is not subclassable"
        )

    def execute(
        self,
        *,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
        reservation_result: ExperimentalWorkflowPureActionReservationResult,
        cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
        invocation_outcome: ExperimentalWorkflowPureActionInvocationOutcome,
        firing_outcome: ExperimentalWorkflowPureActionFiringOutcome,
    ) -> ExperimentalWorkflowPureActionCommitResult:
        """Write legacy compact-only state after source revalidation."""
        candidate = _prepare_commit_candidate(
            authorized_inputs=authorized_inputs,
            reservation_result=reservation_result,
            cpn_plan=cpn_plan,
            invocation_outcome=invocation_outcome,
            firing_outcome=firing_outcome,
        )
        existing = self._reservation_service.load_commit(
            candidate.reservation.identity
        )
        if existing is not None:
            if existing == candidate.coordinates:
                return ExperimentalWorkflowPureActionCommitResult(
                    status=ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT,
                    commit=candidate.commit,
                    diagnostics=(),
                )
            return ExperimentalWorkflowPureActionCommitResult(
                status=ExperimentalWorkflowPureActionCommitStatus.CONFLICT,
                commit=None,
                diagnostics=("conflict",),
            )
        source_status = self._reservation_service.revalidate_sources(
            candidate.authorized
        )
        if source_status is not None:
            return ExperimentalWorkflowPureActionCommitResult(
                status=ExperimentalWorkflowPureActionCommitStatus.STALE,
                commit=None,
                diagnostics=(source_status.value,),
            )
        status = self._reservation_service.commit(
            candidate.reservation,
            candidate.coordinates,
            candidate.record,
        )
        return _commit_result(candidate.commit, status)


def _prepare_commit_candidate(
    *,
    authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
    reservation_result: ExperimentalWorkflowPureActionReservationResult,
    cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
    invocation_outcome: ExperimentalWorkflowPureActionInvocationOutcome,
    firing_outcome: ExperimentalWorkflowPureActionFiringOutcome,
) -> _PreparedCommitCandidate:
    authorized = reconstruct_authorized_inputs(authorized_inputs)
    reservation, _ = reconstruct_successful_reservation(
        reservation_result,
        authorized,
        operation="commit",
    )
    plan = reconstruct_cpn_plan(cpn_plan)
    invocation = _reconstruct_invocation_outcome(invocation_outcome)
    firing = _reconstruct_firing_outcome(firing_outcome)
    commit = _construct_commit(
        authorized=authorized,
        reservation=reservation,
        plan=plan,
        invocation=invocation,
        firing=firing,
    )
    coordinates = ExperimentalWorkflowPureActionCommitCoordinates(
        commit_identity=commit.identity,
        reservation_identity=commit.reservation_identity,
        net_instance_identity=reservation.net_instance_identity,
        predecessor_marking_identity=commit.predecessor_marking_identity,
        predecessor_revision=commit.predecessor_revision,
        successor_marking_identity=commit.successor_marking_identity,
        successor_revision=commit.successor_revision,
    )
    return _PreparedCommitCandidate(
        authorized=authorized,
        reservation=reservation,
        plan=plan,
        invocation=invocation,
        firing=firing,
        commit=commit,
        coordinates=coordinates,
        record=_construct_commit_record(commit, authorized),
    )


def _commit_result(
    commit: ExperimentalWorkflowPureActionCommit,
    status: ExperimentalWorkflowPureActionCommitStatus,
) -> ExperimentalWorkflowPureActionCommitResult:
    if status in {
        ExperimentalWorkflowPureActionCommitStatus.COMMITTED,
        ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT,
    }:
        return ExperimentalWorkflowPureActionCommitResult(
            status=status,
            commit=commit,
            diagnostics=(),
        )
    return ExperimentalWorkflowPureActionCommitResult(
        status=status,
        commit=None,
        diagnostics=(status.value,),
    )


def _construct_commit(
    *,
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs,
    reservation: ExperimentalWorkflowPureActionReservation,
    plan: ExperimentalWorkflowPureActionCpnPlan,
    invocation: ExperimentalWorkflowPureActionInvocationOutcome,
    firing: ExperimentalWorkflowPureActionFiringOutcome,
) -> ExperimentalWorkflowPureActionCommit:
    if reservation.cpn_plan_identity != plan.identity:
        raise ValueError("reservation differs from CPN plan")
    if (
        invocation.status
        is not ExperimentalWorkflowPureActionInvocationStatus.MAPPED
        or invocation.reservation_identity != reservation.identity
        or invocation.input_authorization_identity != authorized.identity
        or invocation.result is None
        or invocation.mapped_result is None
    ):
        raise ValueError("invocation is not an admitted mapped success")
    if (
        firing.status
        is not ExperimentalWorkflowPureActionFiringStatus.FIRED_CANDIDATE
        or firing.cpn_plan_identity != plan.identity
        or firing.invocation_outcome_identity != invocation.identity
        or firing.firing_result is None
        or firing.firing_result.outcome
        is not ColoredPetriNetFiringOutcomeKind.SUCCESS
        or firing.firing_result.successor_marking is None
    ):
        raise ValueError("firing is not a current successful candidate")
    firing_input = firing.firing_result.firing_input
    context = invocation.request.context
    if (
        invocation.request != authorized.admitted_inputs.request
        or firing_input.predecessor_marking.identity.value
        != context.predecessor_marking_identity.value
        or reservation.predecessor_marking_identity
        != context.predecessor_marking_identity
        or reservation.predecessor_revision != context.predecessor_revision
    ):
        raise ValueError("commit state differs from retained predecessor")
    successor = firing.firing_result.successor_marking
    return ExperimentalWorkflowPureActionCommit(
        cpn_plan_identity=plan.identity,
        reservation_identity=reservation.identity,
        input_authorization_identity=authorized.identity,
        source_authority_identities=tuple(
            item.identity for item in authorized.source_authorities
        ),
        invocation_outcome_identity=invocation.identity,
        request_identity=invocation.request.identity,
        owner_result_identity=invocation.result.identity,
        mapped_result_identity=invocation.mapped_result.identity,
        firing_outcome_identity=firing.identity,
        cpn_firing_result_identity=firing.firing_result.identity,
        predecessor_marking_identity=context.predecessor_marking_identity,
        predecessor_revision=context.predecessor_revision,
        successor_marking_identity=WorkflowMarkingIdentity(
            successor.identity.value
        ),
        successor_revision=context.predecessor_revision + 1,
    )


def _construct_commit_record(
    commit: ExperimentalWorkflowPureActionCommit,
    authorized: ExperimentalWorkflowPureActionAuthorizedInputs,
) -> ExperimentalWorkflowPureActionCommitRecord:
    if (
        tuple(item.identity for item in authorized.source_authorities)
        != commit.source_authority_identities
    ):
        raise ValueError(
            "commit source authorities differ from authorized inputs"
        )
    return ExperimentalWorkflowPureActionCommitRecord(
        commit_identity=commit.identity,
        cpn_plan_identity=commit.cpn_plan_identity,
        reservation_identity=commit.reservation_identity,
        net_instance_identity=authorized.admitted_inputs.request.context.net_instance_identity,
        input_authorization_identity=commit.input_authorization_identity,
        source_authorities=authorized.source_authorities,
        invocation_outcome_identity=commit.invocation_outcome_identity.value,
        request_identity=commit.request_identity,
        owner_result_identity=commit.owner_result_identity,
        mapped_result_identity=commit.mapped_result_identity.value,
        firing_outcome_identity=commit.firing_outcome_identity.value,
        cpn_firing_result_identity=commit.cpn_firing_result_identity.value,
        predecessor_marking_identity=commit.predecessor_marking_identity,
        predecessor_revision=commit.predecessor_revision,
        successor_marking_identity=commit.successor_marking_identity,
        successor_revision=commit.successor_revision,
    )


__all__ = [
    "ExperimentalWorkflowPureActionCommit",
    "ExperimentalWorkflowPureActionCommitResult",
    "ExperimentalWorkflowPureActionCommitService",
]
