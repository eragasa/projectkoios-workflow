"""Private synthetic execution-plan closure constructors."""

from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from projectkoios.workflow.petrinet.colored.children.bindings import (
    WorkflowHierarchicalChildBinding,
    WorkflowHierarchicalChildInputMapping,
    WorkflowHierarchicalChildTerminalMapping,
)
from projectkoios.workflow.petrinet.colored.mappings.values import (
    WorkflowValueMappingDescriptor,
)
from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanClosure,
)
from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)
from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
)
from projectkoios.workflow.petrinet.colored.routes.transitions import (
    WorkflowTransitionRoute,
    WorkflowTransitionRouteKind,
)


def value_mapping_descriptor(
    *, adapter_identity: str = "owner-adapter"
) -> WorkflowValueMappingDescriptor:
    """Return one bounded synthetic value mapping."""
    return WorkflowValueMappingDescriptor(
        owner_identity="owner",
        adapter_identity=adapter_identity,
        adapter_version_identity="adapter-version:1",
        input_record_type_identity="owner.input:1",
        output_record_type_identity="cpn.output:1",
        input_payload_schema_identity="input-schema:1",
        input_payload_codec_identity="input-codec:1",
        output_payload_schema_identity="output-schema:1",
        output_payload_codec_identity="output-codec:1",
        correlation_descriptor_identities=("correlation:1",),
        maximum_input_bytes=1024,
        maximum_output_bytes=1024,
        contract_version=1,
    )


def hierarchical_child_binding() -> WorkflowHierarchicalChildBinding:
    """Return one exact v0.1 hierarchical child binding."""
    from _child_export_evidence_fixtures import child_export

    definition, _ = selection_enablement(values=(1,))
    exported_child = child_export()
    route = WorkflowTransitionRoute(
        definition.identity,
        definition.transitions[0].identity,
        WorkflowTransitionRouteKind.HIERARCHICAL_CHILD,
        (),
        None,
        1,
    )
    input_descriptor = value_mapping_descriptor(adapter_identity="child-input")
    output_descriptor = value_mapping_descriptor(
        adapter_identity="child-output"
    )
    requirement = (
        exported_child.closure.interface.terminal_delivery_requirements[0]
    )
    return WorkflowHierarchicalChildBinding(
        parent_definition_identity=definition.identity,
        transition_route=route,
        child_export_identity=exported_child.identity,
        child_execution_plan_identity=exported_child.closure.execution_plan_identity,
        input_mapping=WorkflowHierarchicalChildInputMapping(
            definition.places[0].identity,
            definition.colors[0].identity,
            "child-input-port",
            input_descriptor,
            1,
        ),
        terminal_mappings=(
            WorkflowHierarchicalChildTerminalMapping(
                requirement, output_descriptor, 1
            ),
        ),
        child_instance_cardinality=1,
        child_ordinal=0,
        cancellation_propagation_policy_identity="propagate-none",
        quiescence_required=True,
        maximum_correlation_field_count=8,
        maximum_external_output_reference_count=4,
        contract_version=1,
    )


def execution_plan_closure(
    *, mapping: WorkflowValueMappingDescriptor | None = None
) -> WorkflowExecutionPlanClosure:
    """Return one complete flat plan with an optional owner-adapter route."""
    definition, _ = selection_enablement(values=(1,))
    canonical_definition = CpnCanonicalDefinitionCodec().encode(
        CpnCanonicalDefinitionEncodingInput(definition)
    )
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
        WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
    )
    if mapping is None:
        route = WorkflowTransitionRoute(
            definition.identity,
            definition.transitions[0].identity,
            WorkflowTransitionRouteKind.PURE_CPN,
            (),
            None,
            1,
        )
        mappings: tuple[WorkflowValueMappingDescriptor, ...] = ()
    else:
        route = WorkflowTransitionRoute(
            definition.identity,
            definition.transitions[0].identity,
            WorkflowTransitionRouteKind.OWNER_ADAPTER,
            (mapping,),
            None,
            1,
        )
        mappings = (mapping,)
    return WorkflowExecutionPlanClosure(
        nominal_definition_identity=definition.identity,
        canonical_definition=canonical_definition,
        cpn_execution_profile_identity=profile_identity,
        initial_marking_contract_identity="marking-constructor:1",
        payload_color_bindings=(),
        transition_routes=(route,),
        child_bindings=(),
        child_interface=None,
        terminal_delivery_requirements=(),
        owner_mapping_descriptors=mappings,
        compiler_identity="compiler",
        compiler_version="1",
        contract_version=1,
    )
