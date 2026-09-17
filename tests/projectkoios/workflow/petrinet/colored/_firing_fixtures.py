"""Private synthetic constructors shared by class-owned firing tests."""

from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingSelector,
    ColoredPetriNetDefinition,
    ColoredPetriNetFiringInput,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetToken,
    ColoredPetriNetTransitionEnabler,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)


def predecessor(definition: ColoredPetriNetDefinition) -> ColoredPetriNetMarking:
    """Return the exact one-token predecessor used by selection enablement."""
    token = ColoredPetriNetToken(
        definition.colors[0].identity,
        ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 1),
    )
    return ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("marking"),
        definition.identity,
        (ColoredPetriNetPlaceMarking(definition.places[0].identity, (token,)),),
    )


def firing_input_for(
    definition: ColoredPetriNetDefinition,
    marking: ColoredPetriNetMarking,
    external_values: tuple[ColoredPetriNetValue, ...],
) -> ColoredPetriNetFiringInput:
    """Return a complete canonical firing input for supplied represented state."""
    enablement = ColoredPetriNetTransitionEnabler().execute(definition, marking)
    selection = ColoredPetriNetBindingSelector().execute(definition, enablement)
    assert selection.outcome is ColoredPetriNetSelectionOutcomeKind.SELECTED
    assert selection.selected_binding is not None
    transition = definition.transitions[0]
    external = ColoredPetriNetBinding(
        transition.identity,
        tuple(
            ColoredPetriNetBindingAssignment(variable, value)
            for variable, value in zip(
                transition.external_output_variable_identities,
                external_values,
                strict=True,
            )
        ),
    )
    return ColoredPetriNetFiringInput(
        definition,
        transition.identity,
        marking,
        enablement,
        selection,
        selection.selected_binding,
        None,
        external,
    )


def valid_firing_input() -> ColoredPetriNetFiringInput:
    """Return one complete selected firing with one external output value."""
    definition, _ = selection_enablement(values=(1,))
    return firing_input_for(
        definition,
        predecessor(definition),
        (ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),),
    )
