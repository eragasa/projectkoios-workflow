from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowDeploymentCapabilityPhase,
)


def test_public_contract__is_declared() -> None:
    assert (
        WorkflowDeploymentCapabilityPhase.__name__
        == "WorkflowDeploymentCapabilityPhase"
    )
