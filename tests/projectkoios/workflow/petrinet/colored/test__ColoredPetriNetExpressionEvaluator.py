r"""Software verification of ``ColoredPetriNetExpressionEvaluator``.

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

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetExpressionEvaluator,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = ColoredPetriNetExpressionEvaluator


def expression(
    value: object, kind: ColoredPetriNetValueKind
) -> ColoredPetriNetValueExpression:
    """Evidence ID: Owns no identifier; supports evaluator evidence.

    Requirement: Evaluator tests need explicit literal expressions.

    Acceptance: The helper returns a public literal expression for the supplied value.
    """
    return ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.LITERAL,
        ColoredPetriNetValue(kind, value),  # type: ignore[arg-type]
    )


def binding() -> ColoredPetriNetBinding:
    """Evidence ID: Owns no identifier; supports evaluator evidence.

    Requirement: Evaluator tests need one fixed bound integer variable.

    Acceptance: The helper returns ``x = 2`` under one synthetic transition.
    """
    return ColoredPetriNetBinding(
        ColoredPetriNetTransitionIdentity("transition"),
        (
            ColoredPetriNetBindingAssignment(
                ColoredPetriNetBindingVariableIdentity("x"),
                ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),
            ),
        ),
    )


def test_constructor__subclass_policy__rejects_extension() -> None:
    """Evidence ID: SV-PETRINET-057

    Requirement: The public evaluator cannot acquire domain or Task policy through
    subclass overrides.

    Acceptance: Attempting to define a subclass raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):

        class DomainEvaluator(SUT):  # type: ignore[misc]
            pass


def test_method__evaluate_value__resolves_literal_and_bound_variable() -> None:
    """Evidence ID: SV-PETRINET-047

    Requirement: Value evaluation returns exact literals and nominally bound values.

    Acceptance: The literal is retained by identity and ``x`` resolves exactly to 2.
    """
    evaluator = SUT()
    literal = expression("value", ColoredPetriNetValueKind.STRING)
    variable = ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.VARIABLE,
        variable_identity=ColoredPetriNetBindingVariableIdentity("x"),
    )
    assert evaluator.evaluate_value(literal, binding()) is literal.literal
    assert evaluator.evaluate_value(variable, binding()).value == 2


def test_method__evaluate_value__rejects_absent_variable() -> None:
    """Evidence ID: SV-PETRINET-048

    Requirement: Evaluation never invents an absent variable binding.

    Acceptance: Looking up ``missing`` raises ``KeyError`` exactly.
    """
    variable = ColoredPetriNetValueExpression(
        ColoredPetriNetValueExpressionKind.VARIABLE,
        variable_identity=ColoredPetriNetBindingVariableIdentity("missing"),
    )
    with pytest.raises(KeyError):
        SUT().evaluate_value(variable, binding())


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        pytest.param(ColoredPetriNetGuardOperator.TRUE, True, id="true"),
        pytest.param(ColoredPetriNetGuardOperator.FALSE, False, id="false"),
        pytest.param(ColoredPetriNetGuardOperator.EQUAL, True, id="equal"),
        pytest.param(ColoredPetriNetGuardOperator.NOT_EQUAL, False, id="not_equal"),
        pytest.param(ColoredPetriNetGuardOperator.LESS_THAN, True, id="less_than"),
        pytest.param(
            ColoredPetriNetGuardOperator.LESS_THAN_OR_EQUAL,
            True,
            id="less_than_or_equal",
        ),
        pytest.param(
            ColoredPetriNetGuardOperator.GREATER_THAN,
            False,
            id="greater_than",
        ),
        pytest.param(
            ColoredPetriNetGuardOperator.GREATER_THAN_OR_EQUAL,
            False,
            id="greater_than_or_equal",
        ),
    ],
)
def test_method__evaluate_guard__implements_exact_operators(
    operator: ColoredPetriNetGuardOperator,
    expected: bool,
) -> None:
    """Evidence ID: SV-PETRINET-049

    Requirement: Public guard evaluation implements every constant and comparison
    operator with exact same-kind semantics.

    Acceptance: Every named operator returns the fixed expected Boolean for 1 and 2.
    """
    if operator in {
        ColoredPetriNetGuardOperator.TRUE,
        ColoredPetriNetGuardOperator.FALSE,
    }:
        guard = ColoredPetriNetGuardExpression(operator)
    else:
        guard = ColoredPetriNetGuardExpression(
            operator,
            left=expression(1, ColoredPetriNetValueKind.INTEGER),
            right=expression(
                2 if "than" in operator.value else 1,
                ColoredPetriNetValueKind.INTEGER,
            ),
        )
    assert SUT().evaluate_guard(guard, binding()).value is expected


@pytest.mark.parametrize(
    ("operator", "kind", "left", "right"),
    [
        pytest.param(
            ColoredPetriNetGuardOperator.EQUAL,
            ColoredPetriNetValueKind.BOOLEAN,
            True,
            True,
            id="boolean_equality",
        ),
        pytest.param(
            ColoredPetriNetGuardOperator.EQUAL,
            ColoredPetriNetValueKind.NONE,
            None,
            None,
            id="none_equality",
        ),
        pytest.param(
            ColoredPetriNetGuardOperator.EQUAL,
            ColoredPetriNetValueKind.STRING_SEQUENCE,
            ("a",),
            ("a",),
            id="string_sequence_equality",
        ),
        pytest.param(
            ColoredPetriNetGuardOperator.LESS_THAN,
            ColoredPetriNetValueKind.REAL,
            1.5,
            2.5,
            id="real_ordering",
        ),
        pytest.param(
            ColoredPetriNetGuardOperator.LESS_THAN,
            ColoredPetriNetValueKind.STRING,
            "a",
            "b",
            id="string_ordering",
        ),
    ],
)
def test_method__evaluate_guard__supports_documented_kind_partitions(
    operator: ColoredPetriNetGuardOperator,
    kind: ColoredPetriNetValueKind,
    left: object,
    right: object,
) -> None:
    """Evidence ID: SV-PETRINET-058

    Requirement: Equality supports every closed value kind and ordering supports
    integers, reals, and strings.

    Acceptance: Every named additional kind partition evaluates to exact ``True``.
    """
    guard = ColoredPetriNetGuardExpression(
        operator,
        left=expression(left, kind),
        right=expression(right, kind),
    )
    assert SUT().evaluate_guard(guard, binding()).value is True


def test_method__evaluate_guard__evaluates_boolean_composition() -> None:
    """Evidence ID: SV-PETRINET-050

    Requirement: ``ALL``, ``ANY``, and ``NOT`` recursively evaluate their operands.

    Acceptance: The fixed compositions return exact independently derived Booleans.
    """
    true = ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE)
    false = ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.FALSE)
    evaluator = SUT()
    assert not evaluator.evaluate_guard(
        ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.ALL, (true, false)),
        binding(),
    ).value
    assert evaluator.evaluate_guard(
        ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.ANY, (true, false)),
        binding(),
    ).value
    assert evaluator.evaluate_guard(
        ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.NOT, (false,)),
        binding(),
    ).value


def test_method__evaluate_guard__rejects_incompatible_comparisons() -> None:
    """Evidence ID: SV-PETRINET-051

    Requirement: Comparisons require equal kinds and ordering requires integer, real,
    or string kinds.

    Acceptance: Cross-kind equality and Boolean ordering raise ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT().evaluate_guard(
            ColoredPetriNetGuardExpression(
                ColoredPetriNetGuardOperator.EQUAL,
                left=expression(1, ColoredPetriNetValueKind.INTEGER),
                right=expression(1.0, ColoredPetriNetValueKind.REAL),
            ),
            binding(),
        )
    with pytest.raises(TypeError):
        SUT().evaluate_guard(
            ColoredPetriNetGuardExpression(
                ColoredPetriNetGuardOperator.LESS_THAN,
                left=expression(False, ColoredPetriNetValueKind.BOOLEAN),
                right=expression(True, ColoredPetriNetValueKind.BOOLEAN),
            ),
            binding(),
        )
