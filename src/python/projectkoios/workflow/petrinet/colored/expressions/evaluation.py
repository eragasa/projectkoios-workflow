"""Closed CPN expression evaluation operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ..bindings import CpnBinding
from ..values import (
    CpnControlRecordField,
    CpnControlRecordTypeDefinition,
    CpnValue,
    CpnValueKind,
)
from .grammar import (
    CpnGuardEvaluationResult,
    CpnGuardExpression,
    CpnGuardOperator,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from .collection import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
)
from .construction import (
    CpnControlRecordConstructionInput,
    CpnControlRecordConstructor,
)
from .errors import CpnExpressionOperationError, CpnExpressionOperationErrorCode
from .projection import CpnFieldProjectionInput, CpnFieldProjector
from .validation import (
    CpnExpressionStructureValidationInput,
    CpnExpressionStructureValidator,
)


@dataclass(frozen=True, slots=True)
class CpnExpressionEvaluatorIdentity:
    """Identity of exact four-variant expression evaluation semantics."""

    value: str = "projectkoios.workflow.cpn.expression-evaluator:0.1"


@dataclass(frozen=True, slots=True)
class CpnExpressionEvaluationInput:
    """One expression, binding, and exact retained record schemas."""

    expression: CpnValueExpression
    binding: CpnBinding
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.expression) is not CpnValueExpression:
            raise TypeError("expression must be CpnValueExpression")
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnExpressionEvaluationResult:
    """One exact value produced by pure expression evaluation."""

    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@final
class CpnExpressionEvaluator:
    """Evaluate the closed grammar through public projector/constructor actions."""

    __slots__ = ()

    @property
    def identity(self) -> CpnExpressionEvaluatorIdentity:
        """Return the exact operation identity."""
        return CpnExpressionEvaluatorIdentity()

    def execute(
        self, evaluation_input: CpnExpressionEvaluationInput
    ) -> CpnExpressionEvaluationResult:
        """Evaluate without callbacks, imports, source text, or external access."""
        if type(evaluation_input) is not CpnExpressionEvaluationInput:
            raise CpnExpressionOperationError(
                CpnExpressionOperationErrorCode.INVALID_ARGUMENT,
                (),
                "evaluation_input must be CpnExpressionEvaluationInput",
            )
        structure = CpnExpressionStructureValidator().execute(
            CpnExpressionStructureValidationInput(
                evaluation_input.expression, evaluation_input.type_definitions
            )
        )
        if not structure.is_valid:
            raise structure.issues[0]
        assignments = {
            item.variable_identity: item.value
            for item in evaluation_input.binding.assignments
        }
        values: dict[int, CpnValue] = {}
        stack: list[tuple[CpnValueExpression, bool]] = [
            (evaluation_input.expression, False)
        ]
        while stack:
            expression, ready = stack.pop()
            if not ready:
                stack.append((expression, True))
                if expression.kind is (CpnValueExpressionKind.FIELD_PROJECTION):
                    assert expression.base_expression is not None
                    stack.append((expression.base_expression, False))
                elif expression.kind is (
                    CpnValueExpressionKind.CONTROL_RECORD_CONSTRUCTOR
                ):
                    for field in reversed(expression.constructor_fields):
                        stack.append((field.expression, False))
                continue
            if expression.kind is CpnValueExpressionKind.LITERAL:
                assert expression.literal is not None
                values[id(expression)] = expression.literal
            elif expression.kind is CpnValueExpressionKind.VARIABLE:
                assert expression.variable_identity is not None
                if expression.variable_identity not in assignments:
                    raise CpnExpressionOperationError(
                        CpnExpressionOperationErrorCode.UNBOUND_VARIABLE,
                        (expression.variable_identity.value,),
                        "binding does not contain the requested variable",
                    )
                values[id(expression)] = assignments[
                    expression.variable_identity
                ]
            elif expression.kind is (CpnValueExpressionKind.FIELD_PROJECTION):
                assert expression.base_expression is not None
                values[id(expression)] = (
                    CpnFieldProjector()
                    .execute(
                        CpnFieldProjectionInput(
                            values[id(expression.base_expression)],
                            expression.field_path,
                        )
                    )
                    .value
                )
            else:
                assert expression.record_type_identity is not None
                fields = tuple(
                    CpnControlRecordField(
                        field.identity, values[id(field.expression)]
                    )
                    for field in expression.constructor_fields
                )
                record = (
                    CpnControlRecordConstructor()
                    .execute(
                        CpnControlRecordConstructionInput(
                            expression.record_type_identity,
                            fields,
                            evaluation_input.type_definitions,
                        )
                    )
                    .record
                )
                values[id(expression)] = CpnValue(
                    CpnValueKind.CONTROL_RECORD, record
                )
        return CpnExpressionEvaluationResult(
            values[id(evaluation_input.expression)]
        )


@dataclass(frozen=True, slots=True)
class CpnGuardEvaluationInput:
    """One guard, binding, and retained record schemas."""

    guard: CpnGuardExpression
    binding: CpnBinding
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.guard) is not CpnGuardExpression:
            raise TypeError("guard must be CpnGuardExpression")
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must contain exact type definitions"
            )


@dataclass(frozen=True, slots=True)
class CpnGuardEvaluatorIdentity:
    """Identity of exact closed guard-evaluation semantics."""

    value: str = "projectkoios.workflow.cpn.guard-evaluator:0.1"


@final
class CpnGuardEvaluator:
    """Evaluate closed guards through explicit value-evaluation requests."""

    __slots__ = ()

    @property
    def identity(self) -> CpnGuardEvaluatorIdentity:
        """Return exact guard-evaluation semantics identity."""
        return CpnGuardEvaluatorIdentity()

    def execute(
        self, evaluation_input: CpnGuardEvaluationInput
    ) -> CpnGuardEvaluationResult:
        """Evaluate a closed bounded guard without callbacks."""
        if type(evaluation_input) is not CpnGuardEvaluationInput:
            raise TypeError("evaluation_input must be CpnGuardEvaluationInput")
        guard = evaluation_input.guard
        binding = evaluation_input.binding
        type_definitions = evaluation_input.type_definitions
        CpnGuardExpressionCollector().execute(
            CpnGuardExpressionCollectionInput(guard)
        )
        operator = guard.operator
        if operator is CpnGuardOperator.TRUE:
            return CpnGuardEvaluationResult(True)
        if operator is CpnGuardOperator.FALSE:
            return CpnGuardEvaluationResult(False)
        if operator is CpnGuardOperator.ALL:
            return CpnGuardEvaluationResult(
                all(
                    self.execute(
                        CpnGuardEvaluationInput(item, binding, type_definitions)
                    ).value
                    for item in guard.operands
                )
            )
        if operator is CpnGuardOperator.ANY:
            return CpnGuardEvaluationResult(
                any(
                    self.execute(
                        CpnGuardEvaluationInput(item, binding, type_definitions)
                    ).value
                    for item in guard.operands
                )
            )
        if operator is CpnGuardOperator.NOT:
            return CpnGuardEvaluationResult(
                not self.execute(
                    CpnGuardEvaluationInput(
                        guard.operands[0], binding, type_definitions
                    )
                ).value
            )
        assert guard.left is not None and guard.right is not None
        evaluator = CpnExpressionEvaluator()
        left = evaluator.execute(
            CpnExpressionEvaluationInput(guard.left, binding, type_definitions)
        ).value
        right = evaluator.execute(
            CpnExpressionEvaluationInput(guard.right, binding, type_definitions)
        ).value
        if left.kind is not right.kind:
            raise TypeError("guard comparison requires equal value kinds")
        if operator is CpnGuardOperator.EQUAL:
            return CpnGuardEvaluationResult(left.value == right.value)
        if operator is CpnGuardOperator.NOT_EQUAL:
            return CpnGuardEvaluationResult(left.value != right.value)
        if left.kind not in {
            CpnValueKind.INTEGER,
            CpnValueKind.REAL,
            CpnValueKind.STRING,
        }:
            raise TypeError(
                "ordering guard requires integer, real, or string values"
            )
        if left.kind is CpnValueKind.INTEGER:
            assert type(left.value) is int and type(right.value) is int
            if operator is CpnGuardOperator.LESS_THAN:
                value = left.value < right.value
            elif operator is CpnGuardOperator.LESS_THAN_OR_EQUAL:
                value = left.value <= right.value
            elif operator is CpnGuardOperator.GREATER_THAN:
                value = left.value > right.value
            else:
                value = left.value >= right.value
        elif left.kind is CpnValueKind.REAL:
            assert type(left.value) is float and type(right.value) is float
            if operator is CpnGuardOperator.LESS_THAN:
                value = left.value < right.value
            elif operator is CpnGuardOperator.LESS_THAN_OR_EQUAL:
                value = left.value <= right.value
            elif operator is CpnGuardOperator.GREATER_THAN:
                value = left.value > right.value
            else:
                value = left.value >= right.value
        else:
            assert type(left.value) is str and type(right.value) is str
            if operator is CpnGuardOperator.LESS_THAN:
                value = left.value < right.value
            elif operator is CpnGuardOperator.LESS_THAN_OR_EQUAL:
                value = left.value <= right.value
            elif operator is CpnGuardOperator.GREATER_THAN:
                value = left.value > right.value
            else:
                value = left.value >= right.value
        return CpnGuardEvaluationResult(value)
