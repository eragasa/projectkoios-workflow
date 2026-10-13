"""Nominal tests for ``CpnEnablementResultIdentityDeriverIdentity``."""

from projectkoios.workflow.petrinet.colored.enablement.results.identity import (
    CpnEnablementResultIdentityDeriverIdentity,
)


def test_constructor__uses_fixed_semantic_identity() -> None:
    assert CpnEnablementResultIdentityDeriverIdentity().value.endswith(":0.1")
