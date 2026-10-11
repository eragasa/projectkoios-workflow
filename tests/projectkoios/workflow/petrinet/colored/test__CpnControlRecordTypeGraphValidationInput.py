"""Mirrored public-contract test for :class:`CpnControlRecordTypeGraphValidationInput`."""

from projectkoios.workflow.petrinet.colored.control.records.type_graph import (
    CpnControlRecordTypeGraphValidationInput,
)

SUT = CpnControlRecordTypeGraphValidationInput


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnControlRecordTypeGraphValidationInput"
