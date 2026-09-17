r"""Software verification of ``ColoredPetriNetEnablementResult``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetEnablementResult`` contract.

Facet and represented meaning

Identity-bound complete success or failure for one definition and marking.

Intrinsic and cross-object scope

Nominal correlation and exact closed-variant invariants are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetEnablementFailure,
    ColoredPetriNetEnablementFailureCode,
    ColoredPetriNetEnablementFailureIdentity,
    ColoredPetriNetEnablementResult,
    ColoredPetriNetEnablementResultIdentity,
    ColoredPetriNetExpressionEvaluatorIdentity,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetOrderingPolicyIdentity,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetTransitionEnablerIdentity,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetEnablementResult


def arguments() -> tuple[
    ColoredPetriNetEnablementResultIdentity,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetExpressionEvaluatorIdentity,
    ColoredPetriNetOrderingPolicyIdentity,
    ColoredPetriNetTransitionEnablerIdentity,
]:
    """Evidence ID: Owns no identifier; supports result examples.

    Requirement: Result tests need one fixed tuple of exact nominal identities.

    Acceptance: The helper returns all correlation fields in constructor order.
    """
    return (
        ColoredPetriNetEnablementResultIdentity("0" * 64),
        ColoredPetriNetDefinitionIdentity("definition"),
        ColoredPetriNetSelectionPolicy.DETERMINISTIC_ONLY,
        ColoredPetriNetMarkingIdentity("marking"),
        ColoredPetriNetExpressionEvaluatorIdentity("expression"),
        ColoredPetriNetOrderingPolicyIdentity("ordering"),
        ColoredPetriNetTransitionEnablerIdentity("enabler"),
    )


def test_constructor__outcome__requires_exactly_one_variant() -> None:
    """Evidence ID: SV-PETRINET-096

    Requirement: A result is exactly successful or failed.

    Acceptance: Empty success is valid; absent or simultaneous variants are rejected.
    """
    success = SUT(*arguments(), enabled_bindings=())
    assert success.is_success
    assert success.enabled_bindings == ()
    with pytest.raises(ValueError):
        SUT(*arguments())
    failure = ColoredPetriNetEnablementFailure(
        ColoredPetriNetEnablementFailureIdentity(arguments()[0]),
        ColoredPetriNetEnablementFailureCode.INVALID_MARKING,
        "validation",
        "valid",
        "invalid",
        "not evaluated",
    )
    failed = SUT(*arguments(), failure=failure)
    assert not failed.is_success
    with pytest.raises(ValueError):
        SUT(*arguments(), enabled_bindings=(), failure=failure)


def test_constructor__nominality__rejects_equal_looking_identity() -> None:
    """Evidence ID: SV-PETRINET-097

    Requirement: Correlation fields preserve their exact nominal classes.

    Acceptance: A lexical string in the result-identity position raises ``TypeError``.
    """
    values = arguments()
    with pytest.raises(TypeError):
        SUT("result", *values[1:], enabled_bindings=())  # type: ignore[arg-type]
