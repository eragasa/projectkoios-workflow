from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlan,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert WorkflowExecutionPlan.__name__ == "WorkflowExecutionPlan"
