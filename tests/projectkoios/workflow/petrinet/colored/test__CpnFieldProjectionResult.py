"""Mirrored public-contract test for :class:`CpnFieldProjectionResult`."""

from projectkoios.workflow.petrinet.colored.expressions.projection import (
    CpnFieldProjectionResult,
)

SUT = CpnFieldProjectionResult


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnFieldProjectionResult"
