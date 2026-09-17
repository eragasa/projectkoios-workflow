"""Closed declarative expressions, inscriptions, and pure evaluation.

The generic expression language admits literals and definition-owned bound
variables only. It has no source text, callable, attribute traversal, import,
``eval``, filesystem, network, Workflow, Task, or scientific-policy surface.
Transitions compose input patterns, an optional guard, and output templates;
the public evaluator evaluates only values and guards and grants no firing or
execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, cast, final

from .markings import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingVariableIdentity,
)
from .values import (
    ColoredPetriNetColorIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)


class ColoredPetriNetValueExpressionKind(StrEnum):
    """Closed alternatives for obtaining one generic value.

    Attributes
    ----------
    LITERAL
        Return the expression's exact tagged literal.
    VARIABLE
        Resolve one nominal variable from the supplied transition binding.
    """

    LITERAL = "literal"
    VARIABLE = "variable"


class ColoredPetriNetGuardOperator(StrEnum):
    """Closed Boolean and exact-comparison guard operators."""

    TRUE = "true"
    FALSE = "false"
    ALL = "all"
    ANY = "any"
    NOT = "not"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"


class ColoredPetriNetInputMode(StrEnum):
    """Generic input-inscription token behavior.

    Attributes
    ----------
    CONSUME
        Matching tokens are consumed by successful firing.
    READ
        Matching tokens enable firing but remain in the successor.
    INHIBIT
        Firing is enabled only when no matching token is present.
    """

    CONSUME = "consume"
    READ = "read"
    INHIBIT = "inhibit"


@dataclass(frozen=True, slots=True)
class ColoredPetriNetValueExpression:
    """One closed declarative generic value expression.

    Parameters
    ----------
    kind
        Exact expression discriminant.
    literal
        Tagged literal required only for ``LITERAL``.
    variable_identity
        Nominal binding variable required only for ``VARIABLE``.

    Raises
    ------
    TypeError
        A field has the wrong semantic or nominal type.
    ValueError
        Fields do not match exactly one expression variant.
    """

    kind: ColoredPetriNetValueExpressionKind
    literal: ColoredPetriNetValue | None = None
    variable_identity: ColoredPetriNetBindingVariableIdentity | None = None

    def __post_init__(self) -> None:
        """Enforce one exact closed expression variant."""
        if not isinstance(self.kind, ColoredPetriNetValueExpressionKind):
            raise TypeError("kind must be ColoredPetriNetValueExpressionKind")
        if self.literal is not None and type(self.literal) is not ColoredPetriNetValue:
            raise TypeError("literal must be ColoredPetriNetValue or None")
        if self.variable_identity is not None and (
            type(self.variable_identity) is not ColoredPetriNetBindingVariableIdentity
        ):
            raise TypeError(
                "variable_identity must be ColoredPetriNetBindingVariableIdentity "
                "or None"
            )
        valid = (
            self.kind is ColoredPetriNetValueExpressionKind.LITERAL
            and self.literal is not None
            and self.variable_identity is None
        ) or (
            self.kind is ColoredPetriNetValueExpressionKind.VARIABLE
            and self.literal is None
            and self.variable_identity is not None
        )
        if not valid:
            raise ValueError("expression fields do not match its kind")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetGuardExpression:
    """One pure Boolean expression with operator-specific arity.

    Parameters
    ----------
    operator
        Closed Boolean or comparison operator.
    operands
        Ordered nested guards for ``ALL``, ``ANY``, or ``NOT``.
    left, right
        Value expressions required by comparison operators.

    Raises
    ------
    TypeError
        A field has the wrong semantic type.
    ValueError
        Fields violate the selected operator's exact arity.
    """

    operator: ColoredPetriNetGuardOperator
    operands: tuple[ColoredPetriNetGuardExpression, ...] = ()
    left: ColoredPetriNetValueExpression | None = None
    right: ColoredPetriNetValueExpression | None = None

    def __post_init__(self) -> None:
        """Validate closed guard structure and arity."""
        if not isinstance(self.operator, ColoredPetriNetGuardOperator):
            raise TypeError("operator must be ColoredPetriNetGuardOperator")
        if type(self.operands) is not tuple or any(
            type(item) is not ColoredPetriNetGuardExpression for item in self.operands
        ):
            raise TypeError(
                "operands must be a tuple of ColoredPetriNetGuardExpression"
            )
        for name in ("left", "right"):
            value = getattr(self, name)
            if value is not None and type(value) is not ColoredPetriNetValueExpression:
                raise TypeError(
                    f"{name} must be ColoredPetriNetValueExpression or None"
                )
        constants = {
            ColoredPetriNetGuardOperator.TRUE,
            ColoredPetriNetGuardOperator.FALSE,
        }
        composites = {
            ColoredPetriNetGuardOperator.ALL,
            ColoredPetriNetGuardOperator.ANY,
        }
        comparisons = (
            set(ColoredPetriNetGuardOperator)
            - constants
            - composites
            - {ColoredPetriNetGuardOperator.NOT}
        )
        if self.operator in constants:
            valid = not self.operands and self.left is None and self.right is None
        elif self.operator in composites:
            valid = bool(self.operands) and self.left is None and self.right is None
        elif self.operator is ColoredPetriNetGuardOperator.NOT:
            valid = len(self.operands) == 1 and self.left is None and self.right is None
        else:
            valid = (
                self.operator in comparisons
                and not self.operands
                and self.left is not None
                and self.right is not None
            )
        if not valid:
            raise ValueError("guard fields do not match operator arity")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTokenPattern:
    """One input variable and its nonempty admitted color set.

    Parameters
    ----------
    variable_identity
        Nominal variable receiving a matched token's value.
    allowed_color_identities
        Nonempty unique color set stored in canonical identity order.

    Raises
    ------
    TypeError
        A field has the wrong nominal type.
    ValueError
        The admitted color set is empty or contains duplicates.
    """

    variable_identity: ColoredPetriNetBindingVariableIdentity
    allowed_color_identities: tuple[ColoredPetriNetColorIdentity, ...]

    def __post_init__(self) -> None:
        """Validate nominal fields and canonicalize the admitted color set."""
        if type(self.variable_identity) is not ColoredPetriNetBindingVariableIdentity:
            raise TypeError(
                "variable_identity must be ColoredPetriNetBindingVariableIdentity"
            )
        if type(self.allowed_color_identities) is not tuple or any(
            type(item) is not ColoredPetriNetColorIdentity
            for item in self.allowed_color_identities
        ):
            raise TypeError(
                "allowed_color_identities must be a tuple of "
                "ColoredPetriNetColorIdentity"
            )
        if not self.allowed_color_identities:
            raise ValueError("allowed_color_identities must not be empty")
        if len(set(self.allowed_color_identities)) != len(
            self.allowed_color_identities
        ):
            raise ValueError("allowed_color_identities must be unique")
        object.__setattr__(
            self,
            "allowed_color_identities",
            tuple(sorted(self.allowed_color_identities, key=lambda item: item.value)),
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetInhibitorPattern:
    """One nonbinding color predicate for an inhibitor input arc.

    Parameters
    ----------
    allowed_color_identities
        Nonempty unique color set stored in canonical identity order.

    Raises
    ------
    TypeError
        The admitted colors are not an immutable nominal color tuple.
    ValueError
        The admitted color set is empty or contains duplicates.

    Notes
    -----
    Successful inhibition means no matching token exists, so this pattern cannot
    introduce a bound variable.
    """

    allowed_color_identities: tuple[ColoredPetriNetColorIdentity, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the nonbinding admitted color set."""
        if type(self.allowed_color_identities) is not tuple or any(
            type(item) is not ColoredPetriNetColorIdentity
            for item in self.allowed_color_identities
        ):
            raise TypeError(
                "allowed_color_identities must be a tuple of "
                "ColoredPetriNetColorIdentity"
            )
        if not self.allowed_color_identities:
            raise ValueError("allowed_color_identities must not be empty")
        if len(set(self.allowed_color_identities)) != len(
            self.allowed_color_identities
        ):
            raise ValueError("allowed_color_identities must be unique")
        object.__setattr__(
            self,
            "allowed_color_identities",
            tuple(sorted(self.allowed_color_identities, key=lambda item: item.value)),
        )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetInputInscription:
    """Ordered multiset demand for one generic input arc.

    Parameters
    ----------
    mode
        Consume, read, or inhibitor behavior.
    patterns
        Nonempty ordered pattern demand. Consume/read modes require binding
        ``ColoredPetriNetTokenPattern`` members. Inhibitor mode requires nonbinding
        ``ColoredPetriNetInhibitorPattern`` members because successful absence
        cannot produce a variable value. Order and duplicates are meaningful.

    Raises
    ------
    TypeError
        The mode, tuple, or pattern variant has the wrong semantic type.
    ValueError
        The pattern tuple is empty.
    """

    mode: ColoredPetriNetInputMode
    patterns: tuple[ColoredPetriNetTokenPattern | ColoredPetriNetInhibitorPattern, ...]

    def __post_init__(self) -> None:
        """Validate exact mode and immutable nonempty pattern demand."""
        if not isinstance(self.mode, ColoredPetriNetInputMode):
            raise TypeError("mode must be ColoredPetriNetInputMode")
        if type(self.patterns) is not tuple:
            raise TypeError("patterns must be a tuple")
        if not self.patterns:
            raise ValueError("patterns must not be empty")
        expected_type = (
            ColoredPetriNetInhibitorPattern
            if self.mode is ColoredPetriNetInputMode.INHIBIT
            else ColoredPetriNetTokenPattern
        )
        if any(type(item) is not expected_type for item in self.patterns):
            raise TypeError(
                f"{self.mode.value} patterns must be {expected_type.__name__}"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetTokenTemplate:
    """Declarative template for one produced generic token.

    Parameters
    ----------
    color_identity
        Nominal color of the produced token.
    value_expression
        Expression producing its tagged value.
    token_identity_expression
        Optional expression that must evaluate to a string when firing requires an
        individually correlated output token. Validation occurs during firing.

    Raises
    ------
    TypeError
        A field has the wrong nominal expression or identity type.
    """

    color_identity: ColoredPetriNetColorIdentity
    value_expression: ColoredPetriNetValueExpression
    token_identity_expression: ColoredPetriNetValueExpression | None = None

    def __post_init__(self) -> None:
        """Validate exact nominal template components."""
        if type(self.color_identity) is not ColoredPetriNetColorIdentity:
            raise TypeError("color_identity must be ColoredPetriNetColorIdentity")
        if type(self.value_expression) is not ColoredPetriNetValueExpression:
            raise TypeError("value_expression must be ColoredPetriNetValueExpression")
        if self.token_identity_expression is not None and (
            type(self.token_identity_expression) is not ColoredPetriNetValueExpression
        ):
            raise TypeError(
                "token_identity_expression must be ColoredPetriNetValueExpression "
                "or None"
            )


@dataclass(frozen=True, slots=True)
class ColoredPetriNetOutputInscription:
    """Nonempty ordered token templates for one generic output arc.

    Parameters
    ----------
    templates
        Immutable nonempty ordered token templates.

    Raises
    ------
    TypeError
        ``templates`` is mutable or contains a wrong semantic type.
    ValueError
        ``templates`` is empty.
    """

    templates: tuple[ColoredPetriNetTokenTemplate, ...]

    def __post_init__(self) -> None:
        """Require an immutable nonempty ordered template tuple."""
        if type(self.templates) is not tuple or any(
            type(item) is not ColoredPetriNetTokenTemplate for item in self.templates
        ):
            raise TypeError("templates must be a tuple of ColoredPetriNetTokenTemplate")
        if not self.templates:
            raise ValueError("templates must not be empty")


@dataclass(frozen=True, slots=True)
class ColoredPetriNetGuardEvaluationResult:
    """Immutable result of one successful pure guard evaluation.

    Parameters
    ----------
    value
        Exact built-in Boolean result.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in Boolean.
    """

    value: bool

    def __post_init__(self) -> None:
        """Require an exact built-in Boolean."""
        if type(self.value) is not bool:
            raise TypeError("value must be bool")


@final
class ColoredPetriNetExpressionEvaluator:
    """ActionObject for deterministic generic value and guard evaluation.

    The evaluator is public so enablement, firing, replay, and independent
    inspection can bind the exact operation explicitly. It is stateless, closed,
    non-subclass-policy-bearing, and grants no transition, Task, or effect authority.
    """

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Reject subclass-injected expression or domain policy."""
        raise TypeError(
            "ColoredPetriNetExpressionEvaluator does not support subclasses"
        )

    def evaluate_value(
        self,
        expression: ColoredPetriNetValueExpression,
        binding: ColoredPetriNetBinding,
    ) -> ColoredPetriNetValue:
        """Evaluate one literal or bound-variable expression.

        Raises
        ------
        TypeError
            An argument has the wrong nominal type.
        KeyError
            The requested variable is absent from ``binding``.
        """
        if type(expression) is not ColoredPetriNetValueExpression:
            raise TypeError("expression must be ColoredPetriNetValueExpression")
        if type(binding) is not ColoredPetriNetBinding:
            raise TypeError("binding must be ColoredPetriNetBinding")
        if expression.kind is ColoredPetriNetValueExpressionKind.LITERAL:
            assert expression.literal is not None
            return expression.literal
        assert expression.variable_identity is not None
        assignments = {
            item.variable_identity: item.value for item in binding.assignments
        }
        return assignments[expression.variable_identity]

    def evaluate_guard(
        self,
        guard: ColoredPetriNetGuardExpression,
        binding: ColoredPetriNetBinding,
    ) -> ColoredPetriNetGuardEvaluationResult:
        """Evaluate one pure guard with strict equal-kind comparison semantics.

        Raises
        ------
        TypeError
            An argument has the wrong type, comparison kinds differ, or ordering is
            requested for a non-orderable value kind.
        KeyError
            A requested variable is absent from ``binding``.
        """
        if type(guard) is not ColoredPetriNetGuardExpression:
            raise TypeError("guard must be ColoredPetriNetGuardExpression")
        if type(binding) is not ColoredPetriNetBinding:
            raise TypeError("binding must be ColoredPetriNetBinding")
        operator = guard.operator
        if operator is ColoredPetriNetGuardOperator.TRUE:
            return ColoredPetriNetGuardEvaluationResult(True)
        if operator is ColoredPetriNetGuardOperator.FALSE:
            return ColoredPetriNetGuardEvaluationResult(False)
        if operator is ColoredPetriNetGuardOperator.ALL:
            return ColoredPetriNetGuardEvaluationResult(
                all(self.evaluate_guard(item, binding).value for item in guard.operands)
            )
        if operator is ColoredPetriNetGuardOperator.ANY:
            return ColoredPetriNetGuardEvaluationResult(
                any(self.evaluate_guard(item, binding).value for item in guard.operands)
            )
        if operator is ColoredPetriNetGuardOperator.NOT:
            return ColoredPetriNetGuardEvaluationResult(
                not self.evaluate_guard(guard.operands[0], binding).value
            )
        assert guard.left is not None and guard.right is not None
        left = self.evaluate_value(guard.left, binding)
        right = self.evaluate_value(guard.right, binding)
        if left.kind is not right.kind:
            raise TypeError("guard comparison requires equal value kinds")
        if operator is ColoredPetriNetGuardOperator.EQUAL:
            return ColoredPetriNetGuardEvaluationResult(left.value == right.value)
        if operator is ColoredPetriNetGuardOperator.NOT_EQUAL:
            return ColoredPetriNetGuardEvaluationResult(left.value != right.value)
        if left.kind not in {
            ColoredPetriNetValueKind.INTEGER,
            ColoredPetriNetValueKind.REAL,
            ColoredPetriNetValueKind.STRING,
        }:
            raise TypeError("ordering guard requires integer, real, or string values")
        left_ordered = cast(Any, left.value)
        right_ordered = cast(Any, right.value)
        if operator is ColoredPetriNetGuardOperator.LESS_THAN:
            value = left_ordered < right_ordered
        elif operator is ColoredPetriNetGuardOperator.LESS_THAN_OR_EQUAL:
            value = left_ordered <= right_ordered
        elif operator is ColoredPetriNetGuardOperator.GREATER_THAN:
            value = left_ordered > right_ordered
        else:
            value = left_ordered >= right_ordered
        return ColoredPetriNetGuardEvaluationResult(value)
