from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
    WorkflowCpnExecutionProfileResolutionRequest,
)


def test_constructor__retains_complete_profile() -> None:
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    assert (
        WorkflowCpnExecutionProfileResolutionRequest(profile).profile == profile
    )
