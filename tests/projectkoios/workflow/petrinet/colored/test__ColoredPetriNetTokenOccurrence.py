r"""Software verification of ``ColoredPetriNetTokenOccurrence``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetTokenOccurrence`` contract.

Facet and represented meaning

Exact predecessor token occurrence used by an input pattern.

Intrinsic and cross-object scope

Canonical nonnegative occurrence coordinates are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored import ColoredPetriNetTokenOccurrence

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetTokenOccurrence


def test_constructor__coordinates__rejects_negative_ordinal() -> None:
    """Evidence ID: SV-PETRINET-131

    Requirement: Occurrence coordinates are exact and nonnegative.

    Acceptance: A valid coordinate is retained and negative ordinal rejected.
    """
    firing_input = valid_firing_input()
    arc = firing_input.definition.arcs[0]
    token = firing_input.predecessor_marking.places[0].tokens[0]
    assert SUT(arc.identity, arc.place_identity, 0, 0, token).token == token
    with pytest.raises(ValueError):
        SUT(arc.identity, arc.place_identity, 0, -1, token)
