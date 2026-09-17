r"""Software verification of ``ColoredPetriNetTokenTemplate``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetTokenTemplate`` generic
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

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetTokenTemplate


def literal() -> ColoredPetriNetValueExpression:
    """Return one literal expression; this helper owns no identifier.

    Evidence ID: Helper owns no identifier.

    Requirement: Support template tests without an independent evidence claim.

    Acceptance: Return the public literal ``none`` expression.
    """
    return ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.LITERAL,
        ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
    )


def test_constructor__expressions__preserves_optional_identity_expression() -> None:
    """Evidence ID: SV-PETRINET-056

    Requirement: A template has a nominal color/value expression and optional identity.

    Acceptance: Exact fields store and non-nominal color rejects without coercion.
    """
    expression = literal()
    template = SUT(ColoredPetriNetColorIdentity("color"), expression, expression)
    assert template.value_expression is expression
    assert template.token_identity_expression is expression
    with pytest.raises(TypeError):
        SUT("color", expression)  # type: ignore[arg-type]
