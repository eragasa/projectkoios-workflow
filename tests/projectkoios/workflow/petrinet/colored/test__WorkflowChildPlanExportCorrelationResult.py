from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanExportCorrelationResult,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildPlanExportCorrelationResult.__name__
        == "WorkflowChildPlanExportCorrelationResult"
    )
