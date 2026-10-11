from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileResolver,
)


def test_identity__names_component_resolution_semantics() -> None:
    assert WorkflowCpnExecutionProfileResolver().identity.value.endswith(":0.1")
