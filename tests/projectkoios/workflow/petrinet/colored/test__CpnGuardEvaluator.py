from projectkoios.workflow.petrinet.colored.expressions.evaluation import (
    CpnGuardEvaluator,
)


def test_public_contract__is_declared() -> None:
    assert CpnGuardEvaluator.__name__ == "CpnGuardEvaluator"
