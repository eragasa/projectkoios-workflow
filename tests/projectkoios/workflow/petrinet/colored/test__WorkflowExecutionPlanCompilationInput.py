from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanCompilationInput,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanCompilationInput.__name__
        == "WorkflowExecutionPlanCompilationInput"
    )
