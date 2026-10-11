"""Nominal tests for ``CpnCanonicalMarkingCodecIdentity``."""

from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingCodecIdentity,
)


def test_constructor__uses_fixed_semantic_identity() -> None:
    assert CpnCanonicalMarkingCodecIdentity().value.endswith(":0.1")
