"""Nominal tests for ``CpnShadowFiringReplayerIdentity``."""

from projectkoios.workflow.petrinet.colored.shadow.replay_contracts import (
    CpnShadowFiringReplayerIdentity,
)


def test_constructor__uses_fixed_semantic_identity() -> None:
    assert CpnShadowFiringReplayerIdentity().value.endswith(":0.1")
