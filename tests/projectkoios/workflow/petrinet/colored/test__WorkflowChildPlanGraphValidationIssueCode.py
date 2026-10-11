from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanGraphValidationIssueCode,
)


def test_enum__is_closed_to_static_reference_graph_failures() -> None:
    assert tuple(WorkflowChildPlanGraphValidationIssueCode) == (
        WorkflowChildPlanGraphValidationIssueCode.SELF_REFERENCE,
        WorkflowChildPlanGraphValidationIssueCode.CYCLE,
        WorkflowChildPlanGraphValidationIssueCode.UNREACHABLE_REFERENCE,
    )
