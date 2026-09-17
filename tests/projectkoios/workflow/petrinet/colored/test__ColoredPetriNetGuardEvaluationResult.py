r"""Software verification of ``ColoredPetriNetGuardEvaluationResult``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetGuardEvaluationResult`` generic
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

from projectkoios.workflow.petrinet.colored import ColoredPetriNetGuardEvaluationResult

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetGuardEvaluationResult


def test_constructor__value__requires_exact_boolean() -> None:
    """Evidence ID: SV-PETRINET-055

    Requirement: Guard results contain one exact built-in Boolean.

    Acceptance: Both Booleans retain identity and integer one rejects exactly.
    """
    assert SUT(True).value is True
    assert SUT(False).value is False
    with pytest.raises(TypeError):
        SUT(1)  # type: ignore[arg-type]
