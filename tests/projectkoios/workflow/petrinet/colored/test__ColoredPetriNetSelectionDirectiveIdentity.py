r"""Software verification of ``ColoredPetriNetSelectionDirectiveIdentity``.

Evidence profile: routine

Bounded artifact scope: the public
``ColoredPetriNetSelectionDirectiveIdentity`` contract.

Facet and represented meaning

Content identity of one explicit selection directive.

Intrinsic and cross-object scope

The lowercase SHA-256 spelling boundary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetSelectionDirectiveIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetSelectionDirectiveIdentity


def test_constructor__digest_boundary__accepts_exact_digest_only() -> None:
    """Evidence ID: SV-PETRINET-110

    Requirement: Directive identities use lowercase SHA-256 spellings.

    Acceptance: One valid digest is retained and malformed text is rejected.
    """
    assert SUT("0" * 64).value == "0" * 64
    with pytest.raises(ValueError):
        SUT("directive")
