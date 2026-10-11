"""Nominal tests for ``CpnShadowFiringReplayInput``."""

import pytest

from projectkoios.workflow.petrinet.colored.shadow.replay_contracts import (
    CpnShadowFiringReplayInput,
)


def test_constructor__rejects_arbitrary_roots() -> None:
    with pytest.raises(TypeError):
        CpnShadowFiringReplayInput(object(), object())  # type: ignore[arg-type]
