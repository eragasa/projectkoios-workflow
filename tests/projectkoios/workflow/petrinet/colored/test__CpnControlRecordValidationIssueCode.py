"""Mirrored public-contract test for :class:`CpnControlRecordValidationIssueCode`."""

from projectkoios.workflow.petrinet.colored.control.records.findings import (
    CpnControlRecordValidationIssueCode,
)

SUT = CpnControlRecordValidationIssueCode


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnControlRecordValidationIssueCode"
