from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanExportCorrelationRequest,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildPlanExportCorrelationRequest.__name__
        == "WorkflowChildPlanExportCorrelationRequest"
    )
