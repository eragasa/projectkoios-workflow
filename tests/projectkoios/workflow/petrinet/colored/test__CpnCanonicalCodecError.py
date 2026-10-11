"""Mirrored public-contract test for :class:`CpnCanonicalCodecError`."""

from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
)

SUT = CpnCanonicalCodecError


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnCanonicalCodecError"
