"""Mirrored public-contract test for :class:`CpnValueExpressionCanonicalizationInput`."""

from projectkoios.workflow.petrinet.colored.canonical.expressions.values import (
    CpnValueExpressionCanonicalizationInput,
)

SUT = CpnValueExpressionCanonicalizationInput


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnValueExpressionCanonicalizationInput"
