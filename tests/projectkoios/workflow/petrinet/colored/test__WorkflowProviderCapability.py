from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowProviderCapability,
)


def test_public_contract__is_declared() -> None:
    assert WorkflowProviderCapability.__name__ == "WorkflowProviderCapability"
