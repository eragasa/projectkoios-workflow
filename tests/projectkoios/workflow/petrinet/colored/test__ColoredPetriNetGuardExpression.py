r"""Software verification of ``ColoredPetriNetGuardExpression``.

Evidence profile: routine

Bounded artifact scope: one closed pure Boolean/comparison guard tree.

Facet and represented meaning

The class represents constants, Boolean composition, negation, and exact comparisons.

Intrinsic and cross-object scope

Operator-specific arity and immutable recursive structure are intrinsic. Bound-value
evaluation belongs to ``ColoredPetriNetExpressionEvaluator``.

VVUQ and scientific exclusions

These synthetic checks establish declarative software structure only, not numerical
verification, scientific validation, uncertainty quantification, or authority.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetGuardExpression


def literal(value: int) -> ColoredPetriNetValueExpression:
    """Evidence ID: Owns no identifier; supports guard-expression evidence.

    Requirement: Comparison tests need one explicit integer literal expression.

    Acceptance: The helper returns the corresponding public expression.
    """
    return ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.LITERAL,
        ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, value),
    )


def test_constructor__operator_arity__admits_every_guard_family() -> None:
    """Evidence ID: SV-PETRINET-045

    Requirement: Constants, composites, negation, and binary comparisons have their
    exact documented shapes.

    Acceptance: Representative valid forms from all four families construct exactly.
    """
    true = SUT(ColoredPetriNetGuardOperator.TRUE)
    false = SUT(ColoredPetriNetGuardOperator.FALSE)
    assert SUT(ColoredPetriNetGuardOperator.ALL, (true, false)).operands == (
        true,
        false,
    )
    assert SUT(ColoredPetriNetGuardOperator.NOT, (false,)).operands == (false,)
    assert SUT(
        ColoredPetriNetGuardOperator.EQUAL, left=literal(1), right=literal(1)
    ).left == literal(1)


@pytest.mark.parametrize(
    "guard",
    [
        pytest.param(
            lambda: SUT(
                ColoredPetriNetGuardOperator.TRUE,
                (SUT(ColoredPetriNetGuardOperator.TRUE),),
            ),
            id="constant_with_operand",
        ),
        pytest.param(
            lambda: SUT(ColoredPetriNetGuardOperator.ALL),
            id="empty_composite",
        ),
        pytest.param(
            lambda: SUT(ColoredPetriNetGuardOperator.NOT, ()),
            id="not_without_operand",
        ),
        pytest.param(
            lambda: SUT(ColoredPetriNetGuardOperator.EQUAL, left=literal(1)),
            id="comparison_without_right",
        ),
    ],
)
def test_constructor__operator_arity__rejects_invalid_shapes(guard: object) -> None:
    """Evidence ID: SV-PETRINET-046

    Requirement: Every operator family rejects missing or extra fields.

    Acceptance: Every named malformed constructor raises ``ValueError`` exactly.
    """
    with pytest.raises(ValueError):
        guard()  # type: ignore[operator]
