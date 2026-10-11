from projectkoios.workflow.petrinet.colored.expressions.evaluation import (
    CpnGuardEvaluationInput,
)


def test_public_contract__is_declared() -> None:
    assert CpnGuardEvaluationInput.__name__ == "CpnGuardEvaluationInput"
