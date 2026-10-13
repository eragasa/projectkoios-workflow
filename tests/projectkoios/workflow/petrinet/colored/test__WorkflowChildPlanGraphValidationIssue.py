from projectkoios.workflow.petrinet.colored.deployments.linking.graph import (
    WorkflowChildPlanGraphValidationIssue,
    WorkflowChildPlanGraphValidationIssueCode,
)


def test_constructor__retains_exact_finding_path() -> None:
    issue = WorkflowChildPlanGraphValidationIssue(
        WorkflowChildPlanGraphValidationIssueCode.CYCLE, ("a", "b")
    )
    assert issue.plan_identity_values == ("a", "b")
