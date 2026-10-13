r"""Software verification of ``CpnExpressionEvaluator``.

Evidence profile: routine

Bounded artifact scope: public pure evaluation of closed generic values and guards.

Facet and represented meaning

The ActionObject resolves literal/bound values and evaluates exact Boolean/comparison
guards without firing a transition or invoking a Task.

Intrinsic and cross-object scope

Value lookup, recursive Boolean semantics, strict comparison kinds, ordering domains,
and failures are evaluator-owned. Enablement and firing are excluded.

VVUQ and scientific exclusions

These exact routing checks establish software behavior only, not numerical verification,
scientific validation, uncertainty quantification, authority, or execution.
"""

import pytest

from projectkoios.workflow.petrinet.colored.bindings import (
    CpnBinding,
    CpnBindingAssignment,
)
from projectkoios.workflow.petrinet.colored.definitions import (
    CpnTransitionIdentity,
)
from projectkoios.workflow.petrinet.colored.expressions.evaluation.expressions import (
    CpnExpressionEvaluationInput,
    CpnExpressionEvaluator,
)
from projectkoios.workflow.petrinet.colored.expressions.evaluation.guards import (
    CpnGuardEvaluationInput,
    CpnGuardEvaluator,
)
from projectkoios.workflow.petrinet.colored.expressions.errors import (
    CpnExpressionOperationError,
    CpnExpressionOperationErrorCode,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnGuardExpression,
    CpnGuardOperator,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = CpnExpressionEvaluator


def expression(value: object, kind: CpnValueKind) -> CpnValueExpression:
    """Evidence ID: Owns no identifier; supports evaluator evidence.

    Requirement: Evaluator tests need explicit literal expressions.

    Acceptance: The helper returns a public literal expression for the supplied value.
    """
    return CpnValueExpression(
        CpnValueExpressionKind.LITERAL,
        CpnValue(kind, value),  # type: ignore[arg-type]
    )


def binding() -> CpnBinding:
    """Evidence ID: Owns no identifier; supports evaluator evidence.

    Requirement: Evaluator tests need one fixed bound integer variable.

    Acceptance: The helper returns ``x = 2`` under one synthetic transition.
    """
    return CpnBinding(
        CpnTransitionIdentity("transition"),
        (
            CpnBindingAssignment(
                CpnBindingVariableIdentity("x"),
                CpnValue(CpnValueKind.INTEGER, 2),
            ),
        ),
    )


def test_constructor__subclass_policy__is_statically_final() -> None:
    """The public evaluator declares static finality without a class hook."""
    assert SUT.__final__ is True


def test_method__evaluate_value__resolves_literal_and_bound_variable() -> None:
    """Evidence ID: SV-PETRINET-047

    Requirement: Value evaluation returns exact literals and nominally bound values.

    Acceptance: The literal is retained by identity and ``x`` resolves exactly to 2.
    """
    evaluator = SUT()
    literal = expression("value", CpnValueKind.STRING)
    variable = CpnValueExpression(
        CpnValueExpressionKind.VARIABLE,
        variable_identity=CpnBindingVariableIdentity("x"),
    )
    assert (
        evaluator.execute(
            CpnExpressionEvaluationInput(literal, binding())
        ).value
        is literal.literal
    )
    assert (
        evaluator.execute(
            CpnExpressionEvaluationInput(variable, binding())
        ).value.value
        == 2
    )


def test_method__evaluate_value__rejects_absent_variable() -> None:
    """Evidence ID: SV-PETRINET-048

    Requirement: Evaluation never invents an absent variable binding.

    Acceptance: Looking up ``missing`` raises ``KeyError`` exactly.
    """
    variable = CpnValueExpression(
        CpnValueExpressionKind.VARIABLE,
        variable_identity=CpnBindingVariableIdentity("missing"),
    )
    with pytest.raises(CpnExpressionOperationError) as caught:
        SUT().execute(CpnExpressionEvaluationInput(variable, binding()))
    assert caught.value.code is CpnExpressionOperationErrorCode.UNBOUND_VARIABLE


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        pytest.param(CpnGuardOperator.TRUE, True, id="true"),
        pytest.param(CpnGuardOperator.FALSE, False, id="false"),
        pytest.param(CpnGuardOperator.EQUAL, True, id="equal"),
        pytest.param(CpnGuardOperator.NOT_EQUAL, False, id="not_equal"),
        pytest.param(CpnGuardOperator.LESS_THAN, True, id="less_than"),
        pytest.param(
            CpnGuardOperator.LESS_THAN_OR_EQUAL,
            True,
            id="less_than_or_equal",
        ),
        pytest.param(
            CpnGuardOperator.GREATER_THAN,
            False,
            id="greater_than",
        ),
        pytest.param(
            CpnGuardOperator.GREATER_THAN_OR_EQUAL,
            False,
            id="greater_than_or_equal",
        ),
    ],
)
def test_method__evaluate_guard__implements_exact_operators(
    operator: CpnGuardOperator,
    expected: bool,
) -> None:
    """Evidence ID: SV-PETRINET-049

    Requirement: Public guard evaluation implements every constant and comparison
    operator with exact same-kind semantics.

    Acceptance: Every named operator returns the fixed expected Boolean for 1 and 2.
    """
    if operator in {
        CpnGuardOperator.TRUE,
        CpnGuardOperator.FALSE,
    }:
        guard = CpnGuardExpression(operator)
    else:
        guard = CpnGuardExpression(
            operator,
            left=expression(1, CpnValueKind.INTEGER),
            right=expression(
                2 if "than" in operator.value else 1,
                CpnValueKind.INTEGER,
            ),
        )
    assert (
        CpnGuardEvaluator()
        .execute(CpnGuardEvaluationInput(guard, binding()))
        .value
        is expected
    )


@pytest.mark.parametrize(
    ("operator", "kind", "left", "right"),
    [
        pytest.param(
            CpnGuardOperator.EQUAL,
            CpnValueKind.BOOLEAN,
            True,
            True,
            id="boolean_equality",
        ),
        pytest.param(
            CpnGuardOperator.EQUAL,
            CpnValueKind.NONE,
            None,
            None,
            id="none_equality",
        ),
        pytest.param(
            CpnGuardOperator.EQUAL,
            CpnValueKind.STRING_SEQUENCE,
            ("a",),
            ("a",),
            id="string_sequence_equality",
        ),
        pytest.param(
            CpnGuardOperator.LESS_THAN,
            CpnValueKind.REAL,
            1.5,
            2.5,
            id="real_ordering",
        ),
        pytest.param(
            CpnGuardOperator.LESS_THAN,
            CpnValueKind.STRING,
            "a",
            "b",
            id="string_ordering",
        ),
    ],
)
def test_method__evaluate_guard__supports_documented_kind_partitions(
    operator: CpnGuardOperator,
    kind: CpnValueKind,
    left: object,
    right: object,
) -> None:
    """Evidence ID: SV-PETRINET-058

    Requirement: Equality supports every closed value kind and ordering supports
    integers, reals, and strings.

    Acceptance: Every named additional kind partition evaluates to exact ``True``.
    """
    guard = CpnGuardExpression(
        operator,
        left=expression(left, kind),
        right=expression(right, kind),
    )
    assert (
        CpnGuardEvaluator()
        .execute(CpnGuardEvaluationInput(guard, binding()))
        .value
        is True
    )


def test_method__evaluate_guard__evaluates_boolean_composition() -> None:
    """Evidence ID: SV-PETRINET-050

    Requirement: ``ALL``, ``ANY``, and ``NOT`` recursively evaluate their operands.

    Acceptance: The fixed compositions return exact independently derived Booleans.
    """
    true = CpnGuardExpression(CpnGuardOperator.TRUE)
    false = CpnGuardExpression(CpnGuardOperator.FALSE)
    evaluator = CpnGuardEvaluator()
    assert not evaluator.execute(
        CpnGuardEvaluationInput(
            CpnGuardExpression(CpnGuardOperator.ALL, (true, false)),
            binding(),
        )
    ).value
    assert evaluator.execute(
        CpnGuardEvaluationInput(
            CpnGuardExpression(CpnGuardOperator.ANY, (true, false)),
            binding(),
        )
    ).value
    assert evaluator.execute(
        CpnGuardEvaluationInput(
            CpnGuardExpression(CpnGuardOperator.NOT, (false,)),
            binding(),
        )
    ).value


def test_method__evaluate_guard__rejects_incompatible_comparisons() -> None:
    """Evidence ID: SV-PETRINET-051

    Requirement: Comparisons require equal kinds and ordering requires integer, real,
    or string kinds.

    Acceptance: Cross-kind equality and Boolean ordering raise ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        CpnGuardEvaluator().execute(
            CpnGuardEvaluationInput(
                CpnGuardExpression(
                    CpnGuardOperator.EQUAL,
                    left=expression(1, CpnValueKind.INTEGER),
                    right=expression(1.0, CpnValueKind.REAL),
                ),
                binding(),
            )
        )
    with pytest.raises(TypeError):
        CpnGuardEvaluator().execute(
            CpnGuardEvaluationInput(
                CpnGuardExpression(
                    CpnGuardOperator.LESS_THAN,
                    left=expression(False, CpnValueKind.BOOLEAN),
                    right=expression(True, CpnValueKind.BOOLEAN),
                ),
                binding(),
            )
        )
