"""Mirrored public-contract test for :class:`CpnControlRecordCanonicalDecodingResult`."""

from projectkoios.workflow.petrinet.colored.control.records.canonical import (
    CpnControlRecordCanonicalDecodingResult,
)

SUT = CpnControlRecordCanonicalDecodingResult


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnControlRecordCanonicalDecodingResult"
