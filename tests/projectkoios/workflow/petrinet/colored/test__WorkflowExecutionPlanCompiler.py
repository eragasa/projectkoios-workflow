from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanCompiler,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanCompiler.__name__
        == "WorkflowExecutionPlanCompiler"
    )
