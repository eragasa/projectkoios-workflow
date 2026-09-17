r"""Software verification of ``ColoredPetriNetPlaceDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetPlaceDefinition`` generic
colored-Petri-net contract.

Facet and represented meaning

The class represents its documented immutable data or deterministic action boundary.

Intrinsic and cross-object scope

The focused class contract is covered; enablement and firing remain excluded.

VVUQ and scientific exclusions

These synthetic checks establish software behavior only, not numerical verification,
scientific validation, UQ, authority, execution, or human acceptance.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetPlaceIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetPlaceDefinition


def test_constructor__allowed_colors__canonicalizes_unique_nonempty_set() -> None:
    """Evidence ID: SV-PETRINET-082

    Requirement: A place admits a canonical nonempty unique color set.

    Acceptance: Reversed colors sort; empty and duplicate tuples reject exactly.
    """
    a = ColoredPetriNetColorIdentity("a")
    b = ColoredPetriNetColorIdentity("b")
    place = SUT(ColoredPetriNetPlaceIdentity("place"), (b, a))
    assert place.allowed_color_identities == (a, b)
    with pytest.raises(ValueError):
        SUT(place.identity, ())
    with pytest.raises(ValueError):
        SUT(place.identity, (a, a))
