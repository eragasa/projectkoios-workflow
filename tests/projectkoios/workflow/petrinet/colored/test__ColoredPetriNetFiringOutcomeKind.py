r"""Software verification of ``ColoredPetriNetFiringOutcomeKind``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetFiringOutcomeKind`` enum.

Facet and represented meaning

Closed pure-firing success or failure variants.

Intrinsic and cross-object scope

The exact outcome vocabulary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetFiringOutcomeKind

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetFiringOutcomeKind


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-127

    Requirement: Firing has exactly success and failure outcomes.

    Acceptance: Names and values equal the fixed oracle.
    """
    assert tuple((item.name, item.value) for item in SUT) == (
        ("SUCCESS", "success"),
        ("FAILURE", "failure"),
    )
