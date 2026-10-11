from projectkoios.workflow.petrinet.colored.closure_validation import (
    WorkflowCpnClosureCorrelationInput,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnClosureCorrelationInput.__name__
        == "WorkflowCpnClosureCorrelationInput"
    )
