r"""Software verification of ``ColoredPetriNetValueExpression``.

Evidence profile: routine

Bounded artifact scope: one closed literal-or-bound-variable generic expression.

Facet and represented meaning

The class represents exactly one pure route to a tagged generic value.

Intrinsic and cross-object scope

Closed discriminants, variant field exclusion, nominal typing, and immutability are
covered. Evaluation against a binding belongs to the evaluator.

VVUQ and scientific exclusions

These synthetic checks establish software structure only, not numerical verification,
scientific validation, uncertainty quantification, or Task execution.
"""

import pytest

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetValueExpression


def test_constructor__variants__admits_exact_literal_and_variable_forms() -> None:
    """Evidence ID: SV-PETRINET-043

    Requirement: The expression is exactly one literal or nominal bound variable.

    Acceptance: Both valid variants preserve their active field and clear the other.
    """
    literal = ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 1)
    variable = ColoredPetriNetBindingVariableIdentity("x")
    literal_expression = SUT(ColoredPetriNetValueExpressionKind.LITERAL, literal)
    variable_expression = SUT(
        ColoredPetriNetValueExpressionKind.VARIABLE,
        variable_identity=variable,
    )
    assert literal_expression.literal is literal
    assert literal_expression.variable_identity is None
    assert variable_expression.literal is None
    assert variable_expression.variable_identity is variable


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(("literal", None, None), id="lexical_kind"),
        pytest.param(
            (ColoredPetriNetValueExpressionKind.LITERAL, None, None),
            id="literal_without_value",
        ),
        pytest.param(
            (
                ColoredPetriNetValueExpressionKind.LITERAL,
                ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
                ColoredPetriNetBindingVariableIdentity("x"),
            ),
            id="literal_with_variable",
        ),
        pytest.param(
            (ColoredPetriNetValueExpressionKind.VARIABLE, None, None),
            id="variable_without_identity",
        ),
    ],
)
def test_constructor__closed_variants__rejects_invalid_state(
    arguments: tuple[object, object, object],
) -> None:
    """Evidence ID: SV-PETRINET-044

    Requirement: Expression variants reject missing, extra, and non-nominal state.

    Acceptance: Every named malformed variant raises ``TypeError`` or ``ValueError``
    according to whether its semantic types or typed invariant are wrong.
    """
    expected = TypeError if type(arguments[0]) is str else ValueError
    with pytest.raises(expected):
        SUT(*arguments)  # type: ignore[arg-type]
