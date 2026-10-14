"""Construct and validate one minimal flat colored Petri net."""

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
from projectkoios.workflow.petrinet.colored.validation.definitions.complete import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValueKind,
)


def build_definition() -> CpnDefinition:
    """Build a one-place net whose transition replaces one integer token."""
    color = CpnColorDefinition(
        CpnColorIdentity("integer"),
        (CpnValueKind.INTEGER,),
    )
    place = CpnPlaceDefinition(
        CpnPlaceIdentity("numbers"),
        (color.identity,),
    )
    input_variable = CpnBindingVariableIdentity("input")
    output_variable = CpnBindingVariableIdentity("output")
    transition = CpnTransitionDefinition(
        CpnTransitionIdentity("replace"),
        (input_variable,),
        (output_variable,),
        CpnGuardExpression(CpnGuardOperator.TRUE),
    )
    input_arc = CpnArcDefinition(
        CpnArcIdentity("consume-number"),
        place.identity,
        transition.identity,
        CpnInputInscription(
            CpnInputMode.CONSUME,
            (CpnTokenPattern(input_variable, (color.identity,)),),
        ),
    )
    output_arc = CpnArcDefinition(
        CpnArcIdentity("produce-number"),
        place.identity,
        transition.identity,
        output_inscription=CpnOutputInscription(
            (
                CpnTokenTemplate(
                    color.identity,
                    CpnValueExpression(
                        CpnValueExpressionKind.VARIABLE,
                        variable_identity=output_variable,
                    ),
                ),
            )
        ),
    )
    return CpnDefinition(
        CpnDefinitionIdentity("example.replace-number"),
        (color,),
        (place,),
        (transition,),
        (input_arc, output_arc),
        (transition.identity,),
    )


def main() -> None:
    """Validate the complete immutable definition."""
    definition = build_definition()
    result = CpnDefinitionValidator().execute(
        CpnDefinitionValidationRequest(definition)
    )
    if not result.is_valid:
        raise RuntimeError(f"definition findings: {result.issues!r}")
    print(definition.identity.value)


if __name__ == "__main__":
    main()
