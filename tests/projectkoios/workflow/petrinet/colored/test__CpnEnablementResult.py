r"""Software verification of ``CpnEnablementResult``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnEnablementResult`` contract.

Facet and represented meaning

Identity-bound complete success or failure for one definition and marking.

Intrinsic and cross-object scope

Nominal correlation and exact closed-variant invariants are covered.

VVUQ and scientific exclusions

This is software verification, not scientific validation or UQ.
"""

import pytest

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinitionIdentity,
    CpnSelectionPolicy,
)
from projectkoios.workflow.petrinet.colored.enablement.results.definition import (
    CpnEnablementFailure,
    CpnEnablementFailureCode,
    CpnEnablementFailureIdentity,
    CpnEnablementResult,
    CpnEnablementResultIdentity,
    CpnOrderingPolicyIdentity,
    CpnTransitionEnablerIdentity,
)
from projectkoios.workflow.petrinet.colored.expressions.evaluation.expressions import (
    CpnExpressionEvaluatorIdentity,
)
from projectkoios.workflow.petrinet.colored.markings import CpnMarkingIdentity

pytestmark = pytest.mark.software_verification
SUT = CpnEnablementResult


def arguments() -> tuple[
    CpnEnablementResultIdentity,
    CpnDefinitionIdentity,
    CpnSelectionPolicy,
    CpnMarkingIdentity,
    CpnExpressionEvaluatorIdentity,
    CpnOrderingPolicyIdentity,
    CpnTransitionEnablerIdentity,
]:
    """Evidence ID: Owns no identifier; supports result examples.

    Requirement: Result tests need one fixed tuple of exact nominal identities.

    Acceptance: The helper returns all correlation fields in constructor order.
    """
    return (
        CpnEnablementResultIdentity("0" * 64),
        CpnDefinitionIdentity("definition"),
        CpnSelectionPolicy.DETERMINISTIC_ONLY,
        CpnMarkingIdentity("marking"),
        CpnExpressionEvaluatorIdentity("expression"),
        CpnOrderingPolicyIdentity("ordering"),
        CpnTransitionEnablerIdentity("enabler"),
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
    failure = CpnEnablementFailure(
        CpnEnablementFailureIdentity(arguments()[0]),
        CpnEnablementFailureCode.INVALID_MARKING,
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
