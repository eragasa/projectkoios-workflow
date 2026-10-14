r"""Software verification of ``CpnFiringFailure``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnFiringFailure`` contract.

Facet and represented meaning

Structured pure-firing failure with no successor.

Intrinsic and cross-object scope

Stable code and nonempty diagnostic fields are covered.

VVUQ and scientific exclusions

This is software verification, not external execution or scientific validation.
"""

from dataclasses import replace

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored.bindings import CpnBinding
from projectkoios.workflow.petrinet.colored.firing.results.definition import (
    CpnFiringFailure,
)
from projectkoios.workflow.petrinet.colored.firing.transitions import (
    CpnTransitionFirer,
)

pytestmark = pytest.mark.software_verification
SUT = CpnFiringFailure


def test_constructor__structured_failure__retains_code_and_diagnostic() -> None:
    """Evidence ID: SV-PETRINET-137

    Requirement: Failed firing retains structured phase and diagnostic state.

    Acceptance: An external-binding failure is the exact public failure type.
    """
    firing_input = valid_firing_input()
    result = CpnTransitionFirer().execute(
        replace(
            firing_input,
            external_output_binding=CpnBinding(
                firing_input.transition_identity, ()
            ),
        )
    )
    assert type(result.failure) is SUT
    assert result.failure.operation_phase == "external_output_validation"
    assert result.failure.diagnostic == "firing produced no successor"
