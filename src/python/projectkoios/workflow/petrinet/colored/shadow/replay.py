"""Exact retained shadow-firing replay correlation."""

from typing import final

from .contracts import CpnShadowFiringError, CpnShadowFiringErrorCode
from .firing import CpnShadowFirer
from .replay_contracts import (
    CpnShadowFiringReplayInput,
    CpnShadowFiringReplayResult,
    CpnShadowFiringReplayerIdentity,
)


@final
class CpnShadowFiringReplayer:
    """Replay shadow firing and compare every retained result correlation."""

    __slots__ = ()

    @property
    def identity(self) -> CpnShadowFiringReplayerIdentity:
        """Return exact replay-comparison semantics identity."""
        return CpnShadowFiringReplayerIdentity()

    def execute(
        self, replay_input: CpnShadowFiringReplayInput
    ) -> CpnShadowFiringReplayResult:
        """Return a closed mismatch rather than accepting partial correlation."""
        if type(replay_input) is not CpnShadowFiringReplayInput:
            raise TypeError("replay_input must be CpnShadowFiringReplayInput")
        try:
            replayed = CpnShadowFirer().execute(replay_input.firing_input)
        except CpnShadowFiringError as error:
            return CpnShadowFiringReplayResult(False, None, error.code)
        if replayed != replay_input.retained_result:
            return CpnShadowFiringReplayResult(
                False,
                replayed,
                CpnShadowFiringErrorCode.RETAINED_RESULT_MISMATCH,
            )
        return CpnShadowFiringReplayResult(True, replayed, None)
