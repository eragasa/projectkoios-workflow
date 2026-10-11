"""Private synthetic constructors shared by class-owned selection tests."""

from _validation_fixtures import valid_definition

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinition,
    CpnSelectionPolicy,
)
from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementResult,
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnToken,
    CpnValue,
    CpnValueKind,
)


def selection_definition(
    policy: CpnSelectionPolicy = (CpnSelectionPolicy.DETERMINISTIC_ONLY),
) -> CpnDefinition:
    """Return one structurally valid definition with the requested policy."""
    base = valid_definition()
    return CpnDefinition(
        base.identity,
        base.colors,
        base.places,
        base.transitions,
        base.arcs,
        base.transition_priority,
        policy,
    )


def selection_enablement(
    policy: CpnSelectionPolicy = (CpnSelectionPolicy.DETERMINISTIC_ONLY),
    values: tuple[int, ...] = (2, 1),
) -> tuple[CpnDefinition, CpnEnablementResult]:
    """Return one definition and successful complete enablement result."""
    definition = selection_definition(policy)
    tokens = tuple(
        CpnToken(
            definition.colors[0].identity,
            CpnValue(CpnValueKind.INTEGER, value),
        )
        for value in values
    )
    marking = CpnMarking(
        CpnMarkingIdentity("marking"),
        definition.identity,
        (CpnPlaceMarking(definition.places[0].identity, tokens),),
    )
    return definition, CpnTransitionEnabler().execute(
        CpnTransitionEnablementRequest(definition, marking)
    )
