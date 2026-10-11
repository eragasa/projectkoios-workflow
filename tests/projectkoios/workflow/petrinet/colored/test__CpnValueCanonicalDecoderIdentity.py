"""Mirrored public-contract test for :class:`CpnValueCanonicalDecoderIdentity`."""

from projectkoios.workflow.petrinet.colored.control.records.value_canonical import (
    CpnValueCanonicalDecoderIdentity,
)

SUT = CpnValueCanonicalDecoderIdentity


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnValueCanonicalDecoderIdentity"
