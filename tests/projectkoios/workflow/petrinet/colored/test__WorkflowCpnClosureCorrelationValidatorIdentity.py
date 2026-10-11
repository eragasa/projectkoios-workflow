from projectkoios.workflow.petrinet.colored.closure_validation import (
    WorkflowCpnClosureCorrelationValidatorIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowCpnClosureCorrelationValidatorIdentity.__name__
        == "WorkflowCpnClosureCorrelationValidatorIdentity"
    )
