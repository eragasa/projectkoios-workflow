r"""Software verification of ``ColoredPetriNetProducedToken``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetProducedToken`` contract.

Facet and represented meaning

One produced token and exact output destination coordinate.

Intrinsic and cross-object scope

Nominal fields and nonnegative template index are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored import ColoredPetriNetProducedToken

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetProducedToken


def test_constructor__coordinate__rejects_negative_template_index() -> None:
    """Evidence ID: SV-PETRINET-133

    Requirement: Produced-token output coordinates are exact and nonnegative.

    Acceptance: Zero is accepted and negative index rejected.
    """
    firing_input = valid_firing_input()
    arc = firing_input.definition.arcs[-1]
    token = firing_input.predecessor_marking.places[0].tokens[0]
    assert SUT(arc.identity, arc.place_identity, 0, token).token == token
    with pytest.raises(ValueError):
        SUT(arc.identity, arc.place_identity, -1, token)
