from dataclasses import replace

import pytest

from _child_export_evidence_fixtures import (
    child_execution_plan,
    child_export_evidence_binding,
    child_interface,
)
from _deployment_fixtures import execution_bindings
from _plan_fixtures import execution_plan_closure, hierarchical_child_binding
from projectkoios.workflow.petrinet.colored.children.bindings import (
    WorkflowHierarchicalChildBinding,
)
from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowCompanionProductionPhase,
)
from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowDeploymentBindingKind,
    WorkflowExecutionBindings,
)
from projectkoios.workflow.petrinet.colored.deployments.linking.graph import (
    WorkflowChildPlanReference,
)
from projectkoios.workflow.petrinet.colored.plans.compilation import (
    WorkflowExecutionPlan,
    WorkflowExecutionPlanCompilationInput,
    WorkflowExecutionPlanCompiler,
)


def _nested_plan(
    child: WorkflowHierarchicalChildBinding,
) -> WorkflowExecutionPlan:
    descriptors = tuple(
        sorted(
            (
                child.input_mapping.mapping_descriptor,
                *(
                    item.parent_external_output_mapping_descriptor
                    for item in child.terminal_mappings
                ),
            ),
            key=lambda item: item.identity,
        )
    )
    return WorkflowExecutionPlanCompiler().execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                execution_plan_closure(),
                transition_routes=(child.transition_route,),
                child_bindings=(child,),
                owner_mapping_descriptors=descriptors,
            )
        )
    )


def _reference(
    plan: WorkflowExecutionPlan,
    child: WorkflowHierarchicalChildBinding,
) -> WorkflowChildPlanReference:
    return WorkflowChildPlanReference(
        plan.identity,
        child.child_execution_plan_identity,
        child.child_export_identity,
        1,
    )


def test_constructor__derives_identity_from_complete_deployment_linking() -> (
    None
):
    source = execution_bindings()
    changed = replace(source, contract_version=2)
    assert source.identity != changed.identity


def test_constructor__accepts_exact_typed_child_export_linking() -> None:
    source = execution_bindings()
    child = hierarchical_child_binding()
    nested_plan = _nested_plan(child)
    evidence = child_export_evidence_binding()
    result = WorkflowExecutionBindings(
        nested_plan,
        source.descriptors,
        (_reference(nested_plan, child),),
        (child_execution_plan(),),
        (evidence,),
        1,
    )
    assert result.execution_plan == nested_plan


def test_constructor__rejects_insufficient_typed_provider_capabilities() -> (
    None
):
    source = execution_bindings()
    child = hierarchical_child_binding()
    nested_plan = _nested_plan(child)
    evidence = child_export_evidence_binding()
    linked = WorkflowExecutionBindings(
        nested_plan,
        source.descriptors,
        (_reference(nested_plan, child),),
        (child_execution_plan(),),
        (evidence,),
        1,
    )
    resolver = next(
        item
        for item in linked.descriptors
        if item.kind is WorkflowDeploymentBindingKind.RESOLVER
    )
    insufficient_resolver = replace(
        resolver,
        capability=replace(
            resolver.capability,
            maximum_total_companion_reference_count=0,
            companion_capabilities=(),
        ),
    )
    changed_descriptors = tuple(
        sorted(
            (
                insufficient_resolver
                if item.kind is WorkflowDeploymentBindingKind.RESOLVER
                else item
                for item in linked.descriptors
            ),
            key=lambda item: item.identity,
        )
    )
    with pytest.raises(ValueError, match="companion delivery bounds"):
        replace(linked, descriptors=changed_descriptors)

    wrong_phase_capability = replace(
        resolver.capability.companion_capabilities[0],
        production_phase=WorkflowCompanionProductionPhase.PRE_TERMINAL_RETAINED,
    )
    wrong_phase_resolver = replace(
        resolver,
        capability=replace(
            resolver.capability,
            companion_capabilities=(wrong_phase_capability,),
        ),
    )
    changed_descriptors = tuple(
        sorted(
            (
                wrong_phase_resolver
                if item.kind is WorkflowDeploymentBindingKind.RESOLVER
                else item
                for item in linked.descriptors
            ),
            key=lambda item: item.identity,
        )
    )
    with pytest.raises(ValueError, match="role, phase, or bound"):
        replace(linked, descriptors=changed_descriptors)

    no_reconciliation_resolver = replace(
        resolver,
        capability=replace(
            resolver.capability,
            reconciliation_capability_identities=(),
        ),
    )
    changed_descriptors = tuple(
        sorted(
            (
                no_reconciliation_resolver
                if item.kind is WorkflowDeploymentBindingKind.RESOLVER
                else item
                for item in linked.descriptors
            ),
            key=lambda item: item.identity,
        )
    )
    with pytest.raises(ValueError, match="reconciliation identities"):
        replace(linked, descriptors=changed_descriptors)

    worker = next(
        item
        for item in linked.descriptors
        if item.kind is WorkflowDeploymentBindingKind.WORKER
    )
    insufficient_worker = replace(
        worker,
        capability=replace(
            worker.capability, protected_effect_capability_identities=()
        ),
    )
    changed_descriptors = tuple(
        sorted(
            (
                insufficient_worker
                if item.kind is WorkflowDeploymentBindingKind.WORKER
                else item
                for item in linked.descriptors
            ),
            key=lambda item: item.identity,
        )
    )
    with pytest.raises(ValueError, match="protected effects"):
        replace(linked, descriptors=changed_descriptors)


def test_constructor__validates_root_plan_interface_capabilities() -> None:
    source = execution_bindings()
    interface = child_interface()
    root_plan = WorkflowExecutionPlanCompiler().execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                execution_plan_closure(),
                child_interface=interface,
                terminal_delivery_requirements=(
                    interface.terminal_delivery_requirements
                ),
            )
        )
    )
    linked = WorkflowExecutionBindings(
        root_plan, source.descriptors, (), (), (), 1
    )
    resolver = next(
        item
        for item in linked.descriptors
        if item.kind is WorkflowDeploymentBindingKind.RESOLVER
    )
    worker = next(
        item
        for item in linked.descriptors
        if item.kind is WorkflowDeploymentBindingKind.WORKER
    )

    insufficient_capabilities = (
        replace(
            resolver.capability,
            maximum_total_companion_reference_count=0,
        ),
        replace(
            resolver.capability,
            companion_capabilities=(
                replace(
                    resolver.capability.companion_capabilities[0],
                    evidence_role_identity="other-role",
                ),
            ),
        ),
        replace(
            resolver.capability,
            companion_capabilities=(
                replace(
                    resolver.capability.companion_capabilities[0],
                    production_phase=(
                        WorkflowCompanionProductionPhase.PRE_TERMINAL_RETAINED
                    ),
                ),
            ),
        ),
        replace(
            resolver.capability,
            companion_capabilities=(
                replace(
                    resolver.capability.companion_capabilities[0],
                    maximum_payload_bytes=1,
                ),
            ),
        ),
        replace(
            resolver.capability,
            reconciliation_capability_identities=(),
        ),
    )
    for capability in insufficient_capabilities:
        changed_resolver = replace(resolver, capability=capability)
        descriptors = tuple(
            sorted(
                (
                    changed_resolver
                    if item.kind is WorkflowDeploymentBindingKind.RESOLVER
                    else item
                    for item in linked.descriptors
                ),
                key=lambda item: item.identity,
            )
        )
        with pytest.raises(ValueError):
            replace(linked, descriptors=descriptors)

    changed_worker = replace(
        worker,
        capability=replace(
            worker.capability, protected_effect_capability_identities=()
        ),
    )
    descriptors = tuple(
        sorted(
            (
                changed_worker
                if item.kind is WorkflowDeploymentBindingKind.WORKER
                else item
                for item in linked.descriptors
            ),
            key=lambda item: item.identity,
        )
    )
    with pytest.raises(ValueError, match="protected effects"):
        replace(linked, descriptors=descriptors)

    protocol_interface = replace(
        interface, execution_protocol_requirement_identity="protocol:2"
    )
    protocol_plan = WorkflowExecutionPlanCompiler().execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                execution_plan_closure(),
                child_interface=protocol_interface,
                terminal_delivery_requirements=(
                    protocol_interface.terminal_delivery_requirements
                ),
            )
        )
    )
    with pytest.raises(ValueError, match="protocol requirements"):
        WorkflowExecutionBindings(
            protocol_plan, source.descriptors, (), (), (), 1
        )

    companion = interface.terminal_delivery_requirements[
        0
    ].companion_requirements[0]
    widened_companion = replace(companion, maximum_reference_count=2)
    widened_delivery = replace(
        interface.terminal_delivery_requirements[0],
        companion_requirements=(widened_companion,),
        maximum_total_companion_reference_count=2,
    )
    widened_interface = replace(
        interface, terminal_delivery_requirements=(widened_delivery,)
    )
    widened_plan = WorkflowExecutionPlanCompiler().execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                execution_plan_closure(),
                child_interface=widened_interface,
                terminal_delivery_requirements=(widened_delivery,),
            )
        )
    )
    narrow_companion = replace(
        resolver.capability.companion_capabilities[0],
        maximum_reference_count=1,
    )
    narrow_resolver = replace(
        resolver,
        capability=replace(
            resolver.capability,
            companion_capabilities=(narrow_companion,),
        ),
    )
    descriptors = tuple(
        sorted(
            (
                narrow_resolver
                if item.kind is WorkflowDeploymentBindingKind.RESOLVER
                else item
                for item in source.descriptors
            ),
            key=lambda item: item.identity,
        )
    )
    with pytest.raises(ValueError, match="role, phase, or bound"):
        WorkflowExecutionBindings(widened_plan, descriptors, (), (), (), 1)


def test_constructor__rejects_missing_typed_child_export_evidence() -> None:
    source = execution_bindings()
    child = hierarchical_child_binding()
    nested_plan = _nested_plan(child)
    with pytest.raises(ValueError, match="exactly resolve"):
        WorkflowExecutionBindings(
            nested_plan,
            source.descriptors,
            (_reference(nested_plan, child),),
            (child_execution_plan(),),
            (),
            1,
        )


def test_constructor__rejects_unknown_exported_input_port() -> None:
    source = execution_bindings()
    child = hierarchical_child_binding()
    child = replace(
        child,
        input_mapping=replace(
            child.input_mapping,
            child_input_port_identity="unknown-child-input-port",
        ),
    )
    nested_plan = _nested_plan(child)
    evidence = child_export_evidence_binding()
    with pytest.raises(ValueError, match="exported input port"):
        WorkflowExecutionBindings(
            nested_plan,
            source.descriptors,
            (_reference(nested_plan, child),),
            (child_execution_plan(),),
            (evidence,),
            1,
        )


def test_constructor__rejects_child_terminal_requirement_substitution() -> None:
    source = execution_bindings()
    child = hierarchical_child_binding()
    mapping = child.terminal_mappings[0]
    substituted_requirement = replace(
        mapping.terminal_delivery_requirement,
        output_mapper_descriptor_identity="substituted-output-mapper",
    )
    child = replace(
        child,
        terminal_mappings=(
            replace(
                mapping,
                terminal_delivery_requirement=substituted_requirement,
            ),
        ),
    )
    nested_plan = _nested_plan(child)
    evidence = child_export_evidence_binding()
    with pytest.raises(ValueError, match="exported requirements"):
        WorkflowExecutionBindings(
            nested_plan,
            source.descriptors,
            (_reference(nested_plan, child),),
            (child_execution_plan(),),
            (evidence,),
            1,
        )


def test_constructor__rejects_child_cancellation_policy_substitution() -> None:
    source = execution_bindings()
    child = replace(
        hierarchical_child_binding(),
        cancellation_propagation_policy_identity="substituted-policy",
    )
    nested_plan = _nested_plan(child)
    evidence = child_export_evidence_binding()
    with pytest.raises(ValueError, match="exported policy"):
        WorkflowExecutionBindings(
            nested_plan,
            source.descriptors,
            (_reference(nested_plan, child),),
            (child_execution_plan(),),
            (evidence,),
            1,
        )


def test_constructor__rejects_unretained_transitive_parent_plan() -> None:
    source = execution_bindings()
    child = hierarchical_child_binding()
    nested_plan = _nested_plan(child)
    first = _reference(nested_plan, child)
    second = WorkflowChildPlanReference(
        child.child_execution_plan_identity,
        nested_plan.identity,
        child.child_export_identity,
        1,
    )
    references = tuple(sorted((first, second), key=lambda item: item.identity))
    with pytest.raises(ValueError, match="retained child plans"):
        replace(
            source,
            execution_plan=nested_plan,
            child_plan_references=references,
        )


def test_constructor__requires_every_single_deployment_role() -> None:
    source = execution_bindings()
    with pytest.raises(ValueError, match="exactly one provider"):
        replace(
            source,
            descriptors=tuple(
                item
                for item in source.descriptors
                if item.kind.value != "provider"
            ),
        )
