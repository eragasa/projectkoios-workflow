"""Authoritative atomic commit with durable pure-CPN replay evidence."""

from __future__ import annotations

from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlan,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionCommitStatus,
    ExperimentalWorkflowPureActionReservationResult,
    ExperimentalWorkflowPureActionReservationService,
)

from .pure_action_commit import (
    ExperimentalWorkflowPureActionCommitResult,
    _commit_result,
    _prepare_commit_candidate,
)
from .pure_action_cpn_replay_bundle import (
    ExperimentalWorkflowPureActionCpnReplayBundleFactory,
)
from .pure_action_cpn_replay_evidence import (
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus,
    experimental_cpn_replay_evidence,
)
from .pure_action_cpn_replay_repository import (
    ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
)
from .pure_action_cpn_replay_serialization import (
    ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec,
)
from .pure_action_firing import ExperimentalWorkflowPureActionFiringOutcome
from .pure_action_invocation import (
    ExperimentalWorkflowPureActionInvocationOutcome,
)


@final
class ExperimentalWorkflowPureActionDurableCpnCommitService:
    """Construct and atomically retain an exact replayable CPN commit."""

    __slots__ = ("_reservation_service", "_repository")

    def __init__(
        self,
        reservation_service: ExperimentalWorkflowPureActionReservationService,
        repository: ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
    ) -> None:
        if (
            type(reservation_service)
            is not ExperimentalWorkflowPureActionReservationService
        ):
            raise TypeError(
                "reservation_service must be "
                "ExperimentalWorkflowPureActionReservationService"
            )
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
        ):
            raise TypeError(
                "repository must implement the replay evidence repository"
            )
        if not reservation_service.owns_repository(repository):
            raise ValueError(
                "reservation service and replay port must own the same "
                "repository"
            )
        self._reservation_service = reservation_service
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError("durable CPN commit service is not subclassable")

    def execute(
        self,
        *,
        authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs,
        reservation_result: ExperimentalWorkflowPureActionReservationResult,
        cpn_plan: ExperimentalWorkflowPureActionCpnPlan,
        invocation_outcome: ExperimentalWorkflowPureActionInvocationOutcome,
        firing_outcome: ExperimentalWorkflowPureActionFiringOutcome,
    ) -> ExperimentalWorkflowPureActionCommitResult:
        """Build replay evidence internally and enter one atomic boundary."""
        candidate = _prepare_commit_candidate(
            authorized_inputs=authorized_inputs,
            reservation_result=reservation_result,
            cpn_plan=cpn_plan,
            invocation_outcome=invocation_outcome,
            firing_outcome=firing_outcome,
        )
        firing_result = candidate.firing.firing_result
        if (
            firing_result is None
        ):  # Defensive: preparation already requires success.
            raise ValueError("firing candidate has no CPN firing result")
        bundle = ExperimentalWorkflowPureActionCpnReplayBundleFactory().execute(
            cpn_plan=candidate.plan,
            firing_result=firing_result,
        )
        bundle_bytes = (
            ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
                bundle
            )
        )
        evidence = experimental_cpn_replay_evidence(
            candidate.record,
            bundle_bytes,
        )
        existing = self._reservation_service.load_commit(
            candidate.reservation.identity
        )
        if existing is not None:
            if existing != candidate.coordinates:
                return _failure(
                    ExperimentalWorkflowPureActionCommitStatus.CONFLICT,
                    "conflict",
                )
            retained = self._repository.load_cpn_replay_evidence(
                candidate.commit.identity
            )
            read_status = (
                ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus
            )
            if (
                retained.status is read_status.FOUND
                and retained.evidence == evidence
            ):
                return _commit_result(
                    candidate.commit,
                    ExperimentalWorkflowPureActionCommitStatus.IDEMPOTENT,
                )
            if retained.status in {
                read_status.ABSENT,
                read_status.FOUND,
            }:
                return _failure(
                    ExperimentalWorkflowPureActionCommitStatus.CONFLICT,
                    "cpn_replay_evidence_conflict",
                )
            return _failure(
                ExperimentalWorkflowPureActionCommitStatus.ERROR,
                retained.diagnostics[0],
            )
        source_status = self._reservation_service.revalidate_sources(
            candidate.authorized
        )
        if source_status is not None:
            return _failure(
                ExperimentalWorkflowPureActionCommitStatus.STALE,
                source_status.value,
            )
        status = self._repository.commit_with_cpn_replay(
            candidate.reservation,
            candidate.coordinates,
            candidate.record,
            evidence,
        )
        return _commit_result(candidate.commit, status)


def _failure(
    status: ExperimentalWorkflowPureActionCommitStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCommitResult:
    return ExperimentalWorkflowPureActionCommitResult(
        status=status,
        commit=None,
        diagnostics=(diagnostic,),
    )


__all__ = ["ExperimentalWorkflowPureActionDurableCpnCommitService"]
