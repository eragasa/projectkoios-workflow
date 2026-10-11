"""Private synthetic constructors shared by class-owned firing tests."""

from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored.bindings import (
    CpnBinding,
    CpnBindingAssignment,
)
from projectkoios.workflow.petrinet.colored.definitions import CpnDefinition
from projectkoios.workflow.petrinet.colored.enablement import (
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from projectkoios.workflow.petrinet.colored.firing import CpnFiringInput
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.selection import (
    CpnBindingSelectionRequest,
    CpnBindingSelector,
    CpnSelectionOutcomeKind,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnToken,
    CpnValue,
    CpnValueKind,
)


def predecessor(definition: CpnDefinition) -> CpnMarking:
    """Return the exact one-token predecessor used by selection enablement."""
    token = CpnToken(
        definition.colors[0].identity,
        CpnValue(CpnValueKind.INTEGER, 1),
    )
    return CpnMarking(
        CpnMarkingIdentity("marking"),
        definition.identity,
        (CpnPlaceMarking(definition.places[0].identity, (token,)),),
    )


def firing_input_for(
    definition: CpnDefinition,
    marking: CpnMarking,
    external_values: tuple[CpnValue, ...],
) -> CpnFiringInput:
    """Return a complete canonical firing input for supplied represented state."""
    enablement = CpnTransitionEnabler().execute(
        CpnTransitionEnablementRequest(definition, marking)
    )
    selection = CpnBindingSelector().execute(
        CpnBindingSelectionRequest(definition, enablement)
    )
    assert selection.outcome is CpnSelectionOutcomeKind.SELECTED
    assert selection.selected_binding is not None
    transition = definition.transitions[0]
    external = CpnBinding(
        transition.identity,
        tuple(
            CpnBindingAssignment(variable, value)
            for variable, value in zip(
                transition.external_output_variable_identities,
                external_values,
                strict=True,
            )
        ),
    )
    return CpnFiringInput(
        definition,
        transition.identity,
        marking,
        enablement,
        selection,
        selection.selected_binding,
        None,
        external,
    )


def valid_firing_input() -> CpnFiringInput:
    """Return one complete selected firing with one external output value."""
    definition, _ = selection_enablement(values=(1,))
    return firing_input_for(
        definition,
        predecessor(definition),
        (CpnValue(CpnValueKind.INTEGER, 2),),
    )
