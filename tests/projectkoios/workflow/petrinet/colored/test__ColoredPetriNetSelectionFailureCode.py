r"""Software verification of ``ColoredPetriNetSelectionFailureCode``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetSelectionFailureCode`` enum.

Facet and represented meaning

Closed machine-readable selection failure vocabulary.

Intrinsic and cross-object scope

The exact stable codes are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetSelectionFailureCode

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetSelectionFailureCode


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-108

    Requirement: Selection failures have stable closed codes.

    Acceptance: Names and values equal the fixed oracle.
    """
    assert tuple((item.name, item.value) for item in SUT) == (
        ("ENABLEMENT_FAILED", "enablement_failed"),
        ("DEFINITION_MISMATCH", "definition_mismatch"),
        ("DIRECTED_SELECTION_PROHIBITED", "directed_selection_prohibited"),
        ("DIRECTIVE_ENABLEMENT_MISMATCH", "directive_enablement_mismatch"),
    )
