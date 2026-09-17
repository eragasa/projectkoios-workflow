r"""Software verification of petrinet.colored nominal identity separation.

Evidence profile: routine

Bounded artifact scope: pairwise separation among owner-local generic identities.

Facet and represented meaning

The artifact represents nominal type separation across distinct identity subjects.

Intrinsic and cross-object scope

Pairwise inequality is covered; each lexical boundary remains class-owned.

VVUQ and scientific exclusions

These synthetic checks establish software identity behavior only, not wire encoding,
scientific validity, UQ, authority, execution, or human acceptance.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetTransitionIdentity,
)

pytestmark = pytest.mark.software_verification


def test_artifact__identity_types__remain_nominally_distinct() -> None:
    """Evidence ID: SV-PETRINET-025

    Requirement: Equal-looking identities for different subjects are not
    interchangeable.

    Acceptance: Five equal lexical values produce pairwise-unequal records.
    """
    identities = (
        ColoredPetriNetDefinitionIdentity("shared"),
        ColoredPetriNetMarkingIdentity("shared"),
        ColoredPetriNetPlaceIdentity("shared"),
        ColoredPetriNetTransitionIdentity("shared"),
        ColoredPetriNetBindingVariableIdentity("shared"),
    )
    assert all(
        left == right if left_index == right_index else left != right
        for left_index, left in enumerate(identities)
        for right_index, right in enumerate(identities)
    )
