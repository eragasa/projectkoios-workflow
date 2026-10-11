"""Nominal tests for ``CpnShadowFirerIdentity``."""

from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFirerIdentity,
)


def test_constructor__uses_fixed_semantic_identity() -> None:
    assert CpnShadowFirerIdentity().value.endswith(":0.1")
