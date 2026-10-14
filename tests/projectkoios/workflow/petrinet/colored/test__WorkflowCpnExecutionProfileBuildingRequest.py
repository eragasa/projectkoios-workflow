from projectkoios.workflow.petrinet.colored.profiles.building import (
    WorkflowCpnExecutionProfileBuildingRequest,
)


def test_constructor__creates_explicit_empty_building_request() -> None:
    assert WorkflowCpnExecutionProfileBuildingRequest() == (
        WorkflowCpnExecutionProfileBuildingRequest()
    )
