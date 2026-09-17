r"""Software verification of ``ColoredPetriNetSelectionOutcomeKind``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetSelectionOutcomeKind`` enum.

Facet and represented meaning

Closed selected, empty, no-match, and failure variants.

Intrinsic and cross-object scope

The exact outcome vocabulary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetSelectionOutcomeKind

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetSelectionOutcomeKind


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-107

    Requirement: Selection outcomes are closed and distinguish absence from failure.

    Acceptance: Names and values equal the fixed oracle.
    """
    assert tuple((item.name, item.value) for item in SUT) == (
        ("SELECTED", "selected"),
        ("EMPTY", "empty"),
        ("NO_MATCH", "no_match"),
        ("FAILURE", "failure"),
    )
