from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanCompilerIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanCompilerIdentity.__name__
        == "WorkflowExecutionPlanCompilerIdentity"
    )
