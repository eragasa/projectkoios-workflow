r"""Software verification of ``ColoredPetriNetSelectionPolicy``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetSelectionPolicy`` enum.

Facet and represented meaning

Definition-owned permission for canonical-only or directed selection.

Intrinsic and cross-object scope

The exact closed policy vocabulary is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetSelectionPolicy

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetSelectionPolicy


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-106

    Requirement: Selection permission uses one closed explicit policy.

    Acceptance: Names and values equal the fixed oracle.
    """
    assert tuple((item.name, item.value) for item in SUT) == (
        ("DETERMINISTIC_ONLY", "deterministic_only"),
        ("DIRECTED_ALLOWED", "directed_allowed"),
    )
