r"""Software verification of ``ColoredPetriNetEnablementFailureCode``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetEnablementFailureCode`` enum.

Facet and represented meaning

Closed machine-readable enablement failure vocabulary.

Intrinsic and cross-object scope

The exact stable code set is covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import ColoredPetriNetEnablementFailureCode

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetEnablementFailureCode


def test_property__members__matches_exact_values() -> None:
    """Evidence ID: SV-PETRINET-093

    Requirement: Enablement has one closed operational failure vocabulary.

    Acceptance: Names and spellings equal the fixed complete oracle.
    """
    assert tuple((item.name, item.value) for item in SUT) == (
        ("INVALID_DEFINITION", "invalid_definition"),
        ("INVALID_MARKING", "invalid_marking"),
        ("UNSUPPORTED_EXPRESSION_EVALUATOR", "unsupported_expression_evaluator"),
        ("UNSUPPORTED_ORDERING_POLICY", "unsupported_ordering_policy"),
        ("GUARD_EVALUATION_FAILED", "guard_evaluation_failed"),
    )
