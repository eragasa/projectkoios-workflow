from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlanIdentityDerivationInput,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowExecutionPlanIdentityDerivationInput.__name__
        == "WorkflowExecutionPlanIdentityDerivationInput"
    )
