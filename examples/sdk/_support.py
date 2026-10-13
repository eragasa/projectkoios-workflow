"""Shared construction for the executable SDK examples."""

from define_validate import build_definition
from projectkoios.workflow.petrinet.colored.bindings import (
    CpnBinding,
    CpnBindingAssignment,
)
from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from projectkoios.workflow.petrinet.colored.definitions import CpnDefinition
from projectkoios.workflow.petrinet.colored.enablement.transitions import (
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from projectkoios.workflow.petrinet.colored.firing.inputs import CpnFiringInput
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanClosure,
)
from projectkoios.workflow.petrinet.colored.profiles.building import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)
from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
)
from projectkoios.workflow.petrinet.colored.routes.transitions import (
    WorkflowTransitionRoute,
    WorkflowTransitionRouteKind,
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


def predecessor_marking(definition: CpnDefinition) -> CpnMarking:
    """Return one represented predecessor marking."""
    token = CpnToken(
        definition.colors[0].identity,
        CpnValue(CpnValueKind.INTEGER, 1),
    )
    return CpnMarking(
        CpnMarkingIdentity("example.predecessor"),
        definition.identity,
        (CpnPlaceMarking(definition.places[0].identity, (token,)),),
    )


def selected_firing_input() -> CpnFiringInput:
    """Enable and select the example transition, then bind its external output."""
    definition = build_definition()
    marking = predecessor_marking(definition)
    enablement = CpnTransitionEnabler().execute(
        CpnTransitionEnablementRequest(definition, marking)
    )
    selection = CpnBindingSelector().execute(
        CpnBindingSelectionRequest(definition, enablement)
    )
    if selection.outcome is not CpnSelectionOutcomeKind.SELECTED:
        raise RuntimeError(f"selection failed: {selection!r}")
    if selection.selected_binding is None:
        raise RuntimeError("selected outcome omitted its binding")
    transition = definition.transitions[0]
    external_output = CpnBinding(
        transition.identity,
        (
            CpnBindingAssignment(
                transition.external_output_variable_identities[0],
                CpnValue(CpnValueKind.INTEGER, 2),
            ),
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
        external_output,
    )


def execution_profile() -> WorkflowCpnExecutionProfile:
    """Build the reviewed local execution profile retained for replay."""
    return WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )


def flat_plan_closure() -> WorkflowExecutionPlanClosure:
    """Build one flat plan closure around the example definition."""
    definition = build_definition()
    canonical_definition = CpnCanonicalDefinitionCodec().encode(
        CpnCanonicalDefinitionEncodingInput(definition)
    )
    profile = execution_profile()
    profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
        WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
    )
    route = WorkflowTransitionRoute(
        definition.identity,
        definition.transitions[0].identity,
        WorkflowTransitionRouteKind.PURE_CPN,
        (),
        None,
        1,
    )
    return WorkflowExecutionPlanClosure(
        nominal_definition_identity=definition.identity,
        canonical_definition=canonical_definition,
        cpn_execution_profile_identity=profile_identity,
        initial_marking_contract_identity="example.marking-constructor:1",
        payload_color_bindings=(),
        transition_routes=(route,),
        child_bindings=(),
        child_interface=None,
        terminal_delivery_requirements=(),
        owner_mapping_descriptors=(),
        compiler_identity="example.plan-compiler",
        compiler_version="1",
        contract_version=1,
    )
