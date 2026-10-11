"""Mirrored public-contract test for :class:`CpnExternalOutputValidationInput`."""

from projectkoios.workflow.petrinet.colored.external_outputs import (
    CpnExternalOutputValidationInput,
)

SUT = CpnExternalOutputValidationInput


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnExternalOutputValidationInput"
