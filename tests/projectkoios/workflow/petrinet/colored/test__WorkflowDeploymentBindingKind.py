from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowDeploymentBindingKind,
)


def test_enum__contains_exact_deployment_roles() -> None:
    assert tuple(WorkflowDeploymentBindingKind) == (
        WorkflowDeploymentBindingKind.PROVIDER,
        WorkflowDeploymentBindingKind.WORKER,
        WorkflowDeploymentBindingKind.ENVIRONMENT,
        WorkflowDeploymentBindingKind.RESOLVER,
    )
