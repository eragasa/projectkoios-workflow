r"""Software verification of ``ColoredPetriNetArcDefinition``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetArcDefinition`` generic
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
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetArcDefinition


def test_constructor__direction_variant__requires_exactly_one_inscription() -> None:
    """Evidence ID: SV-PETRINET-061

    Requirement: Arc direction is represented by exactly one inscription variant.

    Acceptance: Input constructs while absent and duplicated variants reject exactly.
    """
    pattern = ColoredPetriNetTokenPattern(
        ColoredPetriNetBindingVariableIdentity("x"),
        (ColoredPetriNetColorIdentity("color"),),
    )
    inscription = ColoredPetriNetInputInscription(
        ColoredPetriNetInputMode.CONSUME, (pattern,)
    )
    args = (
        ColoredPetriNetArcIdentity("arc"),
        ColoredPetriNetPlaceIdentity("place"),
        ColoredPetriNetTransitionIdentity("transition"),
    )
    assert SUT(*args, inscription).input_inscription is inscription
    with pytest.raises(ValueError):
        SUT(*args)
    expression = ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.LITERAL,
        ColoredPetriNetValue(ColoredPetriNetValueKind.NONE, None),
    )
    output = ColoredPetriNetOutputInscription(
        (
            ColoredPetriNetTokenTemplate(
                ColoredPetriNetColorIdentity("color"), expression
            ),
        )
    )
    with pytest.raises(ValueError):
        SUT(*args, inscription, output_inscription=output)
