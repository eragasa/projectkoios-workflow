r"""Software verification of ``ColoredPetriNetInhibitorEvaluation``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetInhibitorEvaluation`` contract.

Facet and represented meaning

Audited inhibitor matching count at one pattern coordinate.

Intrinsic and cross-object scope

Exact nominal and nonnegative count fields are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored import ColoredPetriNetInhibitorEvaluation

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetInhibitorEvaluation


def test_constructor__matching_count__requires_nonnegative_integer() -> None:
    """Evidence ID: SV-PETRINET-132

    Requirement: Inhibitor audits retain exact nonnegative matching counts.

    Acceptance: Zero is accepted and negative count rejected.
    """
    arc = valid_firing_input().definition.arcs[0]
    assert SUT(arc.identity, arc.place_identity, 0, 0).matching_count == 0
    with pytest.raises(ValueError):
        SUT(arc.identity, arc.place_identity, 0, -1)
