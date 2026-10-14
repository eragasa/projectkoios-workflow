"""Nominal tests for ``CpnShadowFiringReplayResult``."""

import pytest

from projectkoios.workflow.petrinet.colored.shadow.replay.contracts import (
    CpnShadowFiringReplayResult,
)


def test_constructor__rejects_open_mismatch() -> None:
    with pytest.raises(ValueError):
        CpnShadowFiringReplayResult(False, None, None)
