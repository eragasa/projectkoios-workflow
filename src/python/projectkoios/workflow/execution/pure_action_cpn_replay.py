"""Exact in-memory pure refiring from canonical CPN transcripts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionDecoder,
    ExperimentalWorkflowCpnMarkingDecoder,
    experimental_shadow_cpn_execution_profile,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingSelector,
    ColoredPetriNetFiringInput,
    ColoredPetriNetFiringOutcomeKind,
    ColoredPetriNetFiringResult,
    ColoredPetriNetSelectionDirective,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetTransitionEnabler,
    ColoredPetriNetTransitionFirer,
)

from .pure_action_cpn_replay_bundle import (
    ExperimentalWorkflowPureActionCpnReplayBundleIdentity,
    _validate_sha256,
)
from .pure_action_cpn_replay_serialization import (
    ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec,
)


class ExperimentalWorkflowPureActionCpnReplayStatus(StrEnum):
    """Closed result of exact in-memory pure-CPN transcript replay."""

    REPLAYED = "replayed"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayResult:
    """Expose a pure result only after exact transcript refiring."""

    status: ExperimentalWorkflowPureActionCpnReplayStatus
    bundle_identity: (
        ExperimentalWorkflowPureActionCpnReplayBundleIdentity | None
    )
    firing_result: ColoredPetriNetFiringResult | None
    bundle_sha256: str | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionCpnReplayStatus
        ):
            raise TypeError(
                "status must be ExperimentalWorkflowPureActionCpnReplayStatus"
            )
        if type(self.diagnostics) is not tuple or any(
            type(item) is not str or not item or len(item) > 128
            for item in self.diagnostics
        ):
            raise TypeError("diagnostics must contain bounded nonempty strings")
        if (
            self.status
            is ExperimentalWorkflowPureActionCpnReplayStatus.REPLAYED
        ):
            if type(self.bundle_identity) is not (
                ExperimentalWorkflowPureActionCpnReplayBundleIdentity
            ):
                raise TypeError("replayed status requires a bundle identity")
            if type(self.firing_result) is not ColoredPetriNetFiringResult:
                raise TypeError("replayed status requires a firing result")
            _validate_sha256(self.bundle_sha256, "bundle SHA-256")
            if self.diagnostics:
                raise ValueError("replayed status prohibits diagnostics")
        elif (
            self.bundle_identity is not None
            or self.firing_result is not None
            or self.bundle_sha256 is not None
        ):
            raise ValueError("non-replayed status prohibits replayed state")
        elif not self.diagnostics:
            raise ValueError("non-replayed status requires diagnostics")


@final
class ExperimentalWorkflowPureActionCpnReplayService:
    """Decode and refire one pure CPN transcript without owner invocation."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCpnReplayService is not subclassable"
        )

    def execute(
        self, value: bytes
    ) -> ExperimentalWorkflowPureActionCpnReplayResult:
        """Refire only under the exact supported retained profile."""
        try:
            bundle = (
                ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().decode(
                    value
                )
            )
        except (TypeError, ValueError) as exc:
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT,
                str(exc) or "CPN replay bundle decoding failed",
            )
        if (
            bundle.execution_profile
            != experimental_shadow_cpn_execution_profile()
        ):
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.INCOMPATIBLE,
                "CPN execution profile is unsupported",
            )
        try:
            definition = ExperimentalWorkflowCpnDefinitionDecoder().decode(
                bundle.definition_bytes
            )
            predecessor = ExperimentalWorkflowCpnMarkingDecoder().decode(
                bundle.predecessor_marking_bytes
            )
            expected_successor = ExperimentalWorkflowCpnMarkingDecoder().decode(
                bundle.successor_marking_bytes
            )
            enablement = ColoredPetriNetTransitionEnabler().execute(
                definition, predecessor
            )
            directive = None
            if bundle.directive_identity is not None:
                directive = ColoredPetriNetSelectionDirective(
                    enablement.identity,
                    bundle.selected_binding,
                )
                if directive.identity != bundle.directive_identity:
                    raise ValueError("selection directive identity differs")
            selection = ColoredPetriNetBindingSelector().execute(
                definition,
                enablement,
                directive,
            )
            if (
                selection.outcome
                is not ColoredPetriNetSelectionOutcomeKind.SELECTED
                or selection.selected_binding != bundle.selected_binding
            ):
                raise ValueError(
                    "retained binding is not selected during replay"
                )
            firing_input = ColoredPetriNetFiringInput(
                definition=definition,
                transition_identity=bundle.transition_identity,
                predecessor_marking=predecessor,
                enablement_result=enablement,
                selection_result=selection,
                selected_binding=bundle.selected_binding,
                directive_identity=bundle.directive_identity,
                external_output_binding=bundle.external_output_binding,
            )
            result = ColoredPetriNetTransitionFirer().execute(firing_input)
            if (
                result.outcome is not ColoredPetriNetFiringOutcomeKind.SUCCESS
                or result.successor_marking != expected_successor
                or result.identity != bundle.expected_firing_result_identity
            ):
                raise ValueError(
                    "pure CPN refiring differs from retained result"
                )
        except (KeyError, TypeError, ValueError) as exc:
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT,
                str(exc) or "pure CPN refiring failed",
            )
        except Exception:
            return _replay_failure(
                ExperimentalWorkflowPureActionCpnReplayStatus.ERROR,
                "pure CPN replay error",
            )
        return ExperimentalWorkflowPureActionCpnReplayResult(
            status=ExperimentalWorkflowPureActionCpnReplayStatus.REPLAYED,
            bundle_identity=bundle.identity,
            firing_result=result,
            bundle_sha256=sha256(value).hexdigest(),
            diagnostics=(),
        )


def _replay_failure(
    status: ExperimentalWorkflowPureActionCpnReplayStatus,
    diagnostic: str,
) -> ExperimentalWorkflowPureActionCpnReplayResult:
    return ExperimentalWorkflowPureActionCpnReplayResult(
        status=status,
        bundle_identity=None,
        firing_result=None,
        bundle_sha256=None,
        diagnostics=(diagnostic[:128],),
    )


__all__ = [
    "ExperimentalWorkflowPureActionCpnReplayResult",
    "ExperimentalWorkflowPureActionCpnReplayService",
    "ExperimentalWorkflowPureActionCpnReplayStatus",
]
