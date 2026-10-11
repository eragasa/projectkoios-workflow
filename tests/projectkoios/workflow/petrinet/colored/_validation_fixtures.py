"""Private synthetic constructors shared by class-owned validator tests."""

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnArcDefinition,
    CpnArcIdentity,
    CpnColorDefinition,
    CpnDefinition,
    CpnDefinitionIdentity,
    CpnPlaceDefinition,
    CpnPlaceIdentity,
    CpnTransitionDefinition,
    CpnTransitionIdentity,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnGuardExpression,
    CpnGuardOperator,
    CpnInputInscription,
    CpnInputMode,
    CpnOutputInscription,
    CpnTokenPattern,
    CpnTokenTemplate,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValue,
    CpnValueKind,
)


def literal(kind: CpnValueKind, value: object) -> CpnValueExpression:
    """Return one explicit generic literal expression."""
    return CpnValueExpression(
        CpnValueExpressionKind.LITERAL,
        CpnValue(kind, value),  # type: ignore[arg-type]
    )


def variable(name: str) -> CpnValueExpression:
    """Return one nominal variable expression."""
    return CpnValueExpression(
        CpnValueExpressionKind.VARIABLE,
        variable_identity=CpnBindingVariableIdentity(name),
    )


def valid_definition() -> CpnDefinition:
    """Return a complete definition with separated input/external variables."""
    color = CpnColorDefinition(
        CpnColorIdentity("number"),
        (CpnValueKind.INTEGER,),
    )
    place = CpnPlaceDefinition(CpnPlaceIdentity("place"), (color.identity,))
    transition = CpnTransitionDefinition(
        CpnTransitionIdentity("transition"),
        (CpnBindingVariableIdentity("input"),),
        (CpnBindingVariableIdentity("output"),),
        CpnGuardExpression(CpnGuardOperator.TRUE),
    )
    input_arc = CpnArcDefinition(
        CpnArcIdentity("input"),
        place.identity,
        transition.identity,
        CpnInputInscription(
            CpnInputMode.CONSUME,
            (
                CpnTokenPattern(
                    CpnBindingVariableIdentity("input"),
                    (color.identity,),
                ),
            ),
        ),
    )
    output_arc = CpnArcDefinition(
        CpnArcIdentity("output"),
        place.identity,
        transition.identity,
        output_inscription=CpnOutputInscription(
            (CpnTokenTemplate(color.identity, variable("output")),)
        ),
    )
    return CpnDefinition(
        CpnDefinitionIdentity("definition"),
        (color,),
        (place,),
        (transition,),
        (input_arc, output_arc),
        (transition.identity,),
    )
