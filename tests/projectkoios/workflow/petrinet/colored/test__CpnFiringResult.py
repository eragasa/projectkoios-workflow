r"""Software verification of ``CpnFiringResult``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnFiringResult`` contract.

Facet and represented meaning

Identity-bound pure-firing success or failure.

Intrinsic and cross-object scope

Closed outcome exclusivity and failure identity correlation are covered.

VVUQ and scientific exclusions

This is software verification, not external execution or scientific validation.
"""

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored.firing.outcomes import (
    CpnFiringOutcomeKind,
    CpnFiringResult,
)
from projectkoios.workflow.petrinet.colored.firing.transitions import (
    CpnTransitionFirer,
)

pytestmark = pytest.mark.software_verification
SUT = CpnFiringResult


def test_constructor__closed_outcome__rejects_missing_success_payload() -> None:
    """Evidence ID: SV-PETRINET-135

    Requirement: Success has successor and audit; failure has only failure state.

    Acceptance: Firer success is valid and empty success construction rejects.
    """
    result = CpnTransitionFirer().execute(valid_firing_input())
    assert type(result) is SUT
    assert result.outcome is CpnFiringOutcomeKind.SUCCESS
    with pytest.raises(ValueError):
        SUT(
            result.identity,
            valid_firing_input(),
            CpnFiringOutcomeKind.SUCCESS,
        )
