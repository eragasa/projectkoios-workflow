"""Private synthetic constructors shared by class-owned selection tests."""

from _validation_fixtures import valid_definition

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetDefinition,
    ColoredPetriNetEnablementResult,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetToken,
    ColoredPetriNetTransitionEnabler,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)


def selection_definition(
    policy: ColoredPetriNetSelectionPolicy = (
        ColoredPetriNetSelectionPolicy.DETERMINISTIC_ONLY
    ),
) -> ColoredPetriNetDefinition:
    """Return one structurally valid definition with the requested policy."""
    base = valid_definition()
    return ColoredPetriNetDefinition(
        base.identity,
        base.colors,
        base.places,
        base.transitions,
        base.arcs,
        base.transition_priority,
        policy,
    )


def selection_enablement(
    policy: ColoredPetriNetSelectionPolicy = (
        ColoredPetriNetSelectionPolicy.DETERMINISTIC_ONLY
    ),
    values: tuple[int, ...] = (2, 1),
) -> tuple[ColoredPetriNetDefinition, ColoredPetriNetEnablementResult]:
    """Return one definition and successful complete enablement result."""
    definition = selection_definition(policy)
    tokens = tuple(
        ColoredPetriNetToken(
            definition.colors[0].identity,
            ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, value),
        )
        for value in values
    )
    marking = ColoredPetriNetMarking(
        ColoredPetriNetMarkingIdentity("marking"),
        definition.identity,
        (ColoredPetriNetPlaceMarking(definition.places[0].identity, tokens),),
    )
    return definition, ColoredPetriNetTransitionEnabler().execute(definition, marking)
