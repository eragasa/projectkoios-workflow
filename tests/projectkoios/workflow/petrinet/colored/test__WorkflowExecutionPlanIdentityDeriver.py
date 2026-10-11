from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanIdentityDeriver,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanIdentityDeriver.__name__
        == "WorkflowExecutionPlanIdentityDeriver"
    )
