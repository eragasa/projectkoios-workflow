from projectkoios.workflow.petrinet.colored.plans.identities import (
    WorkflowExecutionPlanIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanIdentity.__name__
        == "WorkflowExecutionPlanIdentity"
    )
