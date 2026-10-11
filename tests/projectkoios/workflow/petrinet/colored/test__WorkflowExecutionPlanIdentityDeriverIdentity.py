from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanIdentityDeriverIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanIdentityDeriverIdentity.__name__
        == "WorkflowExecutionPlanIdentityDeriverIdentity"
    )
