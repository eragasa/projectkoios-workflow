"""Mirrored public-contract test for :class:`CpnExternalOutputValidationIssueCode`."""

from projectkoios.workflow.petrinet.colored.external_outputs import (
    CpnExternalOutputValidationIssueCode,
)

SUT = CpnExternalOutputValidationIssueCode


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnExternalOutputValidationIssueCode"
