"""Mirrored public-contract test for :class:`CpnExternalOutputValidationResult`."""

from projectkoios.workflow.petrinet.colored.external_outputs import (
    CpnExternalOutputValidationResult,
)

SUT = CpnExternalOutputValidationResult


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnExternalOutputValidationResult"
