"""Durable loading and pure refiring of CPN replay evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import final

from projectkoios.workflow.petrinet.colored import ColoredPetriNetFiringResult
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitIdentity,
)

from .pure_action_cpn_replay import (
    ExperimentalWorkflowPureActionCpnReplayService,
)
from .pure_action_cpn_replay_evidence import (
    ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus,
)
from .pure_action_cpn_replay_repository import (
    ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
)


class ExperimentalWorkflowPureActionDurableCpnReplayStatus(StrEnum):
    REPLAYED = "replayed"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionDurableCpnReplayResult:
    status: ExperimentalWorkflowPureActionDurableCpnReplayStatus
    firing_result: ColoredPetriNetFiringResult | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionDurableCpnReplayStatus
        ):
            raise TypeError("status must be durable CPN replay status")
        if (
            self.status
            is ExperimentalWorkflowPureActionDurableCpnReplayStatus.REPLAYED
        ):
            if type(self.firing_result) is not ColoredPetriNetFiringResult:
                raise TypeError("replayed status requires a firing result")
            if self.diagnostics:
                raise ValueError("replayed status prohibits diagnostics")
        elif self.firing_result is not None or not self.diagnostics:
            raise ValueError(
                "non-replayed status requires diagnostics and prohibits "
                "a result"
            )


@final
class ExperimentalWorkflowPureActionDurableCpnReplayService:
    """Load one correlated durable transcript and purely refire its CPN."""

    __slots__ = ("_repository",)

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionCpnReplayEvidenceRepository,
        ):
            raise TypeError(
                "repository must implement the replay evidence repository"
            )
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError("durable CPN replay service is not subclassable")

    def execute(
        self, commit_identity: ExperimentalWorkflowPureActionCommitIdentity
    ) -> ExperimentalWorkflowPureActionDurableCpnReplayResult:
        loaded = self._repository.load_cpn_replay_evidence(commit_identity)
        found = ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.FOUND
        if loaded.status is not found:
            return ExperimentalWorkflowPureActionDurableCpnReplayResult(
                status=ExperimentalWorkflowPureActionDurableCpnReplayStatus(
                    loaded.status.value
                ),
                firing_result=None,
                diagnostics=loaded.diagnostics,
            )
        assert loaded.evidence is not None
        replayed = ExperimentalWorkflowPureActionCpnReplayService().execute(
            loaded.evidence.bundle_bytes
        )
        return ExperimentalWorkflowPureActionDurableCpnReplayResult(
            status=ExperimentalWorkflowPureActionDurableCpnReplayStatus(
                replayed.status.value
            ),
            firing_result=replayed.firing_result,
            diagnostics=replayed.diagnostics,
        )


__all__ = [
    "ExperimentalWorkflowPureActionDurableCpnReplayResult",
    "ExperimentalWorkflowPureActionDurableCpnReplayService",
    "ExperimentalWorkflowPureActionDurableCpnReplayStatus",
]
