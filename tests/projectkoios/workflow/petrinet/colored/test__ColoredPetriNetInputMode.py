r"""Software verification of ``ColoredPetriNetInputMode``.

Evidence profile: routine

Bounded artifact scope: the closed generic colored-Petri-net enumeration.

Facet and represented meaning

The class represents the accepted closed vocabulary for its owning contract.

Intrinsic and cross-object scope

Exact member spelling and order are covered. Cross-object behavior is excluded.

VVUQ and scientific exclusions

This synthetic check establishes software vocabulary only, not execution, authority,
scientific validity, UQ, or human acceptance.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetInputMode

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetInputMode


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-079

    Requirement: The public enumeration is closed to the documented exact values.

    Acceptance: Iteration returns the fixed value tuple exactly.
    """
    assert tuple(member.value for member in SUT) == ("consume", "read", "inhibit")
