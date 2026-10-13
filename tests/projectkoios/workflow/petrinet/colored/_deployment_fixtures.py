"""Private synthetic deployment-linking constructors."""

from _plan_fixtures import execution_plan_closure

from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowCompanionProductionPhase,
)
from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowCompanionCapability,
    WorkflowDeploymentBindingDescriptor,
    WorkflowDeploymentBindingKind,
    WorkflowDeploymentCapabilityPhase,
    WorkflowProviderCapability,
    WorkflowExecutionBindings,
)
from projectkoios.workflow.petrinet.colored.plans.compilation import (
    WorkflowExecutionPlanCompilationInput,
    WorkflowExecutionPlanCompiler,
)


def deployment_descriptor(
    kind: WorkflowDeploymentBindingKind,
) -> WorkflowDeploymentBindingDescriptor:
    """Return one exact descriptor for the requested deployment role."""
    phase = {
        WorkflowDeploymentBindingKind.PROVIDER: WorkflowDeploymentCapabilityPhase.PROVISION,
        WorkflowDeploymentBindingKind.WORKER: WorkflowDeploymentCapabilityPhase.EXECUTE,
        WorkflowDeploymentBindingKind.ENVIRONMENT: WorkflowDeploymentCapabilityPhase.ENVIRONMENT,
        WorkflowDeploymentBindingKind.RESOLVER: WorkflowDeploymentCapabilityPhase.RESOLVE_AND_RECONCILE,
    }[kind]
    companion_capability = WorkflowCompanionCapability(
        evidence_role_identity="synthetic-companion-reference",
        production_phase=(
            WorkflowCompanionProductionPhase.POST_TERMINAL_PRE_DELIVERY_RETAINED
        ),
        maximum_payload_bytes=4096,
        maximum_reference_count=16,
        contract_version=1,
    )
    capability = WorkflowProviderCapability(
        capability_name=f"capability:{kind.value}",
        phase=phase,
        maximum_total_companion_reference_count=16,
        companion_capabilities=(companion_capability,),
        protected_effect_capability_identities=("synthetic-calculation",),
        reconciliation_capability_identities=("runtime-reconciliation",),
        protocol_requirement_identities=("protocol:1",),
        contract_version=1,
    )
    return WorkflowDeploymentBindingDescriptor(
        kind=kind,
        owner_identity=f"owner:{kind.value}",
        implementation_identity=f"implementation:{kind.value}",
        version_identity="version:1",
        capability=capability,
        protocol_identity="protocol:1",
        contract_version=1,
    )


def execution_bindings() -> WorkflowExecutionBindings:
    """Return one complete provider/worker/environment/resolver linking."""
    plan = WorkflowExecutionPlanCompiler().execute(
        WorkflowExecutionPlanCompilationInput(execution_plan_closure())
    )
    descriptors = tuple(
        sorted(
            (
                deployment_descriptor(WorkflowDeploymentBindingKind.PROVIDER),
                deployment_descriptor(WorkflowDeploymentBindingKind.WORKER),
                deployment_descriptor(
                    WorkflowDeploymentBindingKind.ENVIRONMENT
                ),
                deployment_descriptor(WorkflowDeploymentBindingKind.RESOLVER),
            ),
            key=lambda item: item.identity,
        )
    )
    return WorkflowExecutionBindings(plan, descriptors, (), (), (), 1)
