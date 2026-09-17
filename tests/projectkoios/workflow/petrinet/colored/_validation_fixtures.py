"""Private synthetic constructors shared by class-owned validator tests."""

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorDefinition,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)


def literal(
    kind: ColoredPetriNetValueKind, value: object
) -> ColoredPetriNetValueExpression:
    """Return one explicit generic literal expression."""
    return ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.LITERAL,
        ColoredPetriNetValue(kind, value),  # type: ignore[arg-type]
    )


def variable(name: str) -> ColoredPetriNetValueExpression:
    """Return one nominal variable expression."""
    return ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.VARIABLE,
        variable_identity=ColoredPetriNetBindingVariableIdentity(name),
    )


def valid_definition() -> ColoredPetriNetDefinition:
    """Return a complete definition with separated input/external variables."""
    color = ColoredPetriNetColorDefinition(
        ColoredPetriNetColorIdentity("number"),
        (ColoredPetriNetValueKind.INTEGER,),
    )
    place = ColoredPetriNetPlaceDefinition(
        ColoredPetriNetPlaceIdentity("place"), (color.identity,)
    )
    transition = ColoredPetriNetTransitionDefinition(
        ColoredPetriNetTransitionIdentity("transition"),
        (ColoredPetriNetBindingVariableIdentity("input"),),
        (ColoredPetriNetBindingVariableIdentity("output"),),
        ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE),
    )
    input_arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("input"),
        place.identity,
        transition.identity,
        ColoredPetriNetInputInscription(
            ColoredPetriNetInputMode.CONSUME,
            (
                ColoredPetriNetTokenPattern(
                    ColoredPetriNetBindingVariableIdentity("input"),
                    (color.identity,),
                ),
            ),
        ),
    )
    output_arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("output"),
        place.identity,
        transition.identity,
        output_inscription=ColoredPetriNetOutputInscription(
            (ColoredPetriNetTokenTemplate(color.identity, variable("output")),)
        ),
    )
    return ColoredPetriNetDefinition(
        ColoredPetriNetDefinitionIdentity("definition"),
        (color,),
        (place,),
        (transition,),
        (input_arc, output_arc),
        (transition.identity,),
    )
