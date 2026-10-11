"""Mirrored public-contract test for :class:`CpnCanonicalDefinitionDecodingInput`."""

from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinitionDecodingInput,
)

SUT = CpnCanonicalDefinitionDecodingInput


def test_public__exact_class_name_is_stable() -> None:
    """The named public contract is directly importable from its candidate owner module for verification."""
    assert SUT.__name__ == "CpnCanonicalDefinitionDecodingInput"
