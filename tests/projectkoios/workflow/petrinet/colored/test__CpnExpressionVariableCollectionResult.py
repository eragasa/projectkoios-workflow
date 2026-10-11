"""Mirrored public-contract test for :class:`CpnExpressionVariableCollectionResult`."""

from projectkoios.workflow.petrinet.colored.expressions.collection import (
    CpnExpressionVariableCollectionResult,
)

SUT = CpnExpressionVariableCollectionResult


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnExpressionVariableCollectionResult"
