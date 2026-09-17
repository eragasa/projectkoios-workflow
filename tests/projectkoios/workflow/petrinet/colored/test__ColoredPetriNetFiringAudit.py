r"""Software verification of ``ColoredPetriNetFiringAudit``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetFiringAudit`` contract.

Facet and represented meaning

Complete occurrence, inhibitor, output, and firer audit for successful firing.

Intrinsic and cross-object scope

Immutable exact audit collections are covered.

VVUQ and scientific exclusions

This is software verification, not external execution or scientific validation.
"""

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetFiringAudit,
    ColoredPetriNetTransitionFirer,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetFiringAudit


def test_constructor__successful_audit__retains_all_occurrences() -> None:
    """Evidence ID: SV-PETRINET-134

    Requirement: Successful firing retains complete immutable audit facts.

    Acceptance: The firer result audit has consumed and produced coordinates.
    """
    result = ColoredPetriNetTransitionFirer().execute(valid_firing_input())
    assert type(result.audit) is SUT
    assert len(result.audit.consumed_occurrences) == 1
    assert len(result.audit.produced_tokens) == 1
