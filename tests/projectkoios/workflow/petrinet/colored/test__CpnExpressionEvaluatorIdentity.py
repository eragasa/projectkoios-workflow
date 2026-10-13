from dataclasses import fields, is_dataclass

from projectkoios.workflow.petrinet.colored.expressions.evaluation import (
    CpnExpressionEvaluatorIdentity,
)

SUT = CpnExpressionEvaluatorIdentity


def test_public_data__is_frozen_slotted_and_typed() -> None:
    assert is_dataclass(SUT)
    assert SUT.__dataclass_params__.frozen
    assert "__slots__" in SUT.__dict__
    declared_fields = fields(SUT)
    assert declared_fields
    assert all(
        item.type not in (object, list, dict) for item in declared_fields
    )
