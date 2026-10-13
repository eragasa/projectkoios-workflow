from projectkoios.workflow.petrinet.colored.profiles.building import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)
from projectkoios.workflow.petrinet.colored.profiles.resolution import (
    WorkflowCpnExecutionProfileResolutionRequest,
)


def test_constructor__retains_complete_profile() -> None:
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    assert (
        WorkflowCpnExecutionProfileResolutionRequest(profile).profile == profile
    )
