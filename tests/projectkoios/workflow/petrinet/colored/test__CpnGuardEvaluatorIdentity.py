from projectkoios.workflow.petrinet.colored.expressions.evaluation import (
    CpnGuardEvaluatorIdentity,
)


def test_public_contract__is_declared() -> None:
    assert CpnGuardEvaluatorIdentity.__name__ == "CpnGuardEvaluatorIdentity"
