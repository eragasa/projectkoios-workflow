"""Mirrored public-contract test for :class:`CpnExpressionCanonicalCodecError`."""

from projectkoios.workflow.petrinet.colored.canonical.expressions.errors import (
    CpnExpressionCanonicalCodecError,
)

SUT = CpnExpressionCanonicalCodecError


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnExpressionCanonicalCodecError"
