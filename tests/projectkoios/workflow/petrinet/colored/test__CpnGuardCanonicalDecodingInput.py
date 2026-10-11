"""Mirrored public-contract test for :class:`CpnGuardCanonicalDecodingInput`."""

from projectkoios.workflow.petrinet.colored.canonical.expressions.guards import (
    CpnGuardCanonicalDecodingInput,
)

SUT = CpnGuardCanonicalDecodingInput


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnGuardCanonicalDecodingInput"
