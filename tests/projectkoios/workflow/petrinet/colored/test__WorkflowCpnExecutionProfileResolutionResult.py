from projectkoios.workflow.petrinet.colored.profiles.building import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)
from projectkoios.workflow.petrinet.colored.profiles.resolution import (
    WorkflowCpnExecutionProfileResolutionRequest,
    WorkflowCpnExecutionProfileResolver,
)


def test_is_available__is_true_only_without_issues() -> None:
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    result = WorkflowCpnExecutionProfileResolver().execute(
        WorkflowCpnExecutionProfileResolutionRequest(profile)
    )
    assert result.is_available is True
