from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanGraphValidationResult,
)


def test_is_valid__is_true_only_without_findings() -> None:
    assert WorkflowChildPlanGraphValidationResult(()).is_valid
