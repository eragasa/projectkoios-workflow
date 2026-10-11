"""Mirrored public-contract test for :class:`CpnGuardCanonicalDecoder`."""

from projectkoios.workflow.petrinet.colored.canonical.expressions.guards import (
    CpnGuardCanonicalDecoder,
)

SUT = CpnGuardCanonicalDecoder


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnGuardCanonicalDecoder"
