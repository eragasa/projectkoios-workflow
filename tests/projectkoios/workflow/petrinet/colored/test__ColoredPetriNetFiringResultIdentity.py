r"""Software verification of ``ColoredPetriNetFiringResultIdentity``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetFiringResultIdentity`` contract.

Facet and represented meaning

Content identity of one closed firing outcome.

Intrinsic and cross-object scope

The lowercase SHA-256 spelling boundary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetFiringResultIdentity

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetFiringResultIdentity


def test_constructor__digest_boundary__accepts_exact_digest_only() -> None:
    """Evidence ID: SV-PETRINET-129

    Requirement: Firing-result identities use lowercase SHA-256 spellings.

    Acceptance: A valid digest is retained and malformed text rejected.
    """
    assert SUT("0" * 64).value == "0" * 64
    with pytest.raises(ValueError):
        SUT("result")
