from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanExportCorrelatorIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowChildPlanExportCorrelatorIdentity.__name__
        == "WorkflowChildPlanExportCorrelatorIdentity"
    )
