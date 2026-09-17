r"""Software verification of ``ColoredPetriNetFiringFailureCode``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetFiringFailureCode`` enum.

Facet and represented meaning

Closed machine-readable pure-firing failure vocabulary.

Intrinsic and cross-object scope

Stable code uniqueness and required members are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetFiringFailureCode

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetFiringFailureCode


def test_property__members__are_unique_and_complete() -> None:
    """Evidence ID: SV-PETRINET-128

    Requirement: Every firing failure has one unique stable code.

    Acceptance: Values are unique and include all derivation/output failure phases.
    """
    values = tuple(item.value for item in SUT)
    assert len(values) == len(set(values)) == 11
    assert "enablement_mismatch" in values
    assert "token_identity_collision" in values
