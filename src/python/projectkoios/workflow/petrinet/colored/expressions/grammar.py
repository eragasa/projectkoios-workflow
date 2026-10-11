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

from ..values import (
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeIdentity,
    CpnColorIdentity,
    CpnValue,
)


@dataclass(frozen=True, slots=True)
class CpnBindingVariableIdentity:
    """Nominal identity of one variable in a transition binding.

    Parameters
    ----------
    value
        Nonempty owner-local lexical identity.

    Raises
    ------
    TypeError
        ``value`` is not an exact built-in string.
    ValueError
        ``value`` is empty.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the exact built-in nonempty string boundary."""
        if type(self.value) is not str:
            raise TypeError("binding variable identity value must be a string")
        if not self.value:
            raise ValueError(
                "binding variable identity value must not be empty"
            )


@dataclass(frozen=True, slots=True)
class CpnExpressionGrammarIdentity:
    """Exact closed expression variants, arities, paths, and bounds identity."""

    value: str = "projectkoios.workflow.cpn.expression-grammar:0.1"


class CpnValueExpressionKind(StrEnum):
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
    FIELD_PROJECTION = "field_projection"
    CONTROL_RECORD_CONSTRUCTOR = "control_record_constructor"


@dataclass(frozen=True, slots=True)
class CpnControlRecordConstructorField:
    """One required field expression in lexical field-identity order."""

    identity: CpnControlRecordFieldIdentity
    expression: CpnValueExpression

    def __post_init__(self) -> None:
        if type(self.identity) is not CpnControlRecordFieldIdentity:
            raise TypeError("identity must be CpnControlRecordFieldIdentity")
        if type(self.expression) is not CpnValueExpression:
            raise TypeError("expression must be CpnValueExpression")


class CpnGuardOperator(StrEnum):
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


class CpnInputMode(StrEnum):
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
class CpnValueExpression:
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

    kind: CpnValueExpressionKind
    literal: CpnValue | None = None
    variable_identity: CpnBindingVariableIdentity | None = None
    base_expression: CpnValueExpression | None = None
    field_path: tuple[CpnControlRecordFieldIdentity, ...] = ()
    record_type_identity: CpnControlRecordTypeIdentity | None = None
    constructor_fields: tuple[CpnControlRecordConstructorField, ...] = ()

    def __post_init__(self) -> None:
        """Enforce one exact closed expression variant."""
        if not isinstance(self.kind, CpnValueExpressionKind):
            raise TypeError("kind must be CpnValueExpressionKind")
        if self.literal is not None and type(self.literal) is not CpnValue:
            raise TypeError("literal must be CpnValue or None")
        if self.variable_identity is not None and (
            type(self.variable_identity) is not CpnBindingVariableIdentity
        ):
            raise TypeError(
                "variable_identity must be CpnBindingVariableIdentity or None"
            )
        if (
            self.base_expression is not None
            and type(self.base_expression) is not CpnValueExpression
        ):
            raise TypeError(
                "base_expression must be CpnValueExpression or None"
            )
        if type(self.field_path) is not tuple or any(
            type(item) is not CpnControlRecordFieldIdentity
            for item in self.field_path
        ):
            raise TypeError(
                "field_path must be a tuple of CpnControlRecordFieldIdentity"
            )
        if (
            self.record_type_identity is not None
            and type(self.record_type_identity)
            is not CpnControlRecordTypeIdentity
        ):
            raise TypeError(
                "record_type_identity must be CpnControlRecordTypeIdentity or None"
            )
        if type(self.constructor_fields) is not tuple or any(
            type(item) is not CpnControlRecordConstructorField
            for item in self.constructor_fields
        ):
            raise TypeError(
                "constructor_fields must be a tuple of "
                "CpnControlRecordConstructorField"
            )
        no_projection = self.base_expression is None and not self.field_path
        no_constructor = (
            self.record_type_identity is None and not self.constructor_fields
        )
        valid = (
            (
                self.kind is CpnValueExpressionKind.LITERAL
                and self.literal is not None
                and self.variable_identity is None
                and no_projection
                and no_constructor
            )
            or (
                self.kind is CpnValueExpressionKind.VARIABLE
                and self.literal is None
                and self.variable_identity is not None
                and no_projection
                and no_constructor
            )
            or (
                self.kind is CpnValueExpressionKind.FIELD_PROJECTION
                and self.literal is None
                and self.variable_identity is None
                and self.base_expression is not None
                and 1 <= len(self.field_path) <= 8
                and no_constructor
            )
            or (
                self.kind is CpnValueExpressionKind.CONTROL_RECORD_CONSTRUCTOR
                and self.literal is None
                and self.variable_identity is None
                and no_projection
                and self.record_type_identity is not None
                and 1 <= len(self.constructor_fields) <= 64
            )
        )
        if not valid:
            raise ValueError("expression fields do not match its kind")
        if self.constructor_fields:
            identities = tuple(
                item.identity.value for item in self.constructor_fields
            )
            if identities != tuple(sorted(identities)):
                raise ValueError(
                    "constructor fields must use lexical identity order"
                )
            if len(set(identities)) != len(identities):
                raise ValueError("constructor field identities must be unique")


@dataclass(frozen=True, slots=True)
class CpnGuardExpression:
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

    operator: CpnGuardOperator
    operands: tuple[CpnGuardExpression, ...] = ()
    left: CpnValueExpression | None = None
    right: CpnValueExpression | None = None

    def __post_init__(self) -> None:
        """Validate closed guard structure and arity."""
        if not isinstance(self.operator, CpnGuardOperator):
            raise TypeError("operator must be CpnGuardOperator")
        if type(self.operands) is not tuple or any(
            type(item) is not CpnGuardExpression for item in self.operands
        ):
            raise TypeError("operands must be a tuple of CpnGuardExpression")
        for name in ("left", "right"):
            value = getattr(self, name)
            if value is not None and type(value) is not CpnValueExpression:
                raise TypeError(f"{name} must be CpnValueExpression or None")
        constants = {
            CpnGuardOperator.TRUE,
            CpnGuardOperator.FALSE,
        }
        composites = {
            CpnGuardOperator.ALL,
            CpnGuardOperator.ANY,
        }
        comparisons = (
            set(CpnGuardOperator)
            - constants
            - composites
            - {CpnGuardOperator.NOT}
        )
        if self.operator in constants:
            valid = (
                not self.operands and self.left is None and self.right is None
            )
        elif self.operator in composites:
            valid = (
                bool(self.operands) and self.left is None and self.right is None
            )
        elif self.operator is CpnGuardOperator.NOT:
            valid = (
                len(self.operands) == 1
                and self.left is None
                and self.right is None
            )
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
class CpnTokenPattern:
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

    variable_identity: CpnBindingVariableIdentity
    allowed_color_identities: tuple[CpnColorIdentity, ...]

    def __post_init__(self) -> None:
        """Validate nominal fields and canonicalize the admitted color set."""
        if type(self.variable_identity) is not CpnBindingVariableIdentity:
            raise TypeError(
                "variable_identity must be CpnBindingVariableIdentity"
            )
        if type(self.allowed_color_identities) is not tuple or any(
            type(item) is not CpnColorIdentity
            for item in self.allowed_color_identities
        ):
            raise TypeError(
                "allowed_color_identities must be a tuple of CpnColorIdentity"
            )
        if not self.allowed_color_identities:
            raise ValueError("allowed_color_identities must not be empty")
        if len(set(self.allowed_color_identities)) != len(
            self.allowed_color_identities
        ):
            raise ValueError("allowed_color_identities must be unique")
        ordered_colors = [
            (item.value, item) for item in self.allowed_color_identities
        ]
        ordered_colors.sort()
        object.__setattr__(
            self,
            "allowed_color_identities",
            tuple(item[1] for item in ordered_colors),
        )


@dataclass(frozen=True, slots=True)
class CpnInhibitorPattern:
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

    allowed_color_identities: tuple[CpnColorIdentity, ...]

    def __post_init__(self) -> None:
        """Validate and canonicalize the nonbinding admitted color set."""
        if type(self.allowed_color_identities) is not tuple or any(
            type(item) is not CpnColorIdentity
            for item in self.allowed_color_identities
        ):
            raise TypeError(
                "allowed_color_identities must be a tuple of CpnColorIdentity"
            )
        if not self.allowed_color_identities:
            raise ValueError("allowed_color_identities must not be empty")
        if len(set(self.allowed_color_identities)) != len(
            self.allowed_color_identities
        ):
            raise ValueError("allowed_color_identities must be unique")
        ordered_colors = [
            (item.value, item) for item in self.allowed_color_identities
        ]
        ordered_colors.sort()
        object.__setattr__(
            self,
            "allowed_color_identities",
            tuple(item[1] for item in ordered_colors),
        )


@dataclass(frozen=True, slots=True)
class CpnInputInscription:
    """Ordered multiset demand for one generic input arc.

    Parameters
    ----------
    mode
        Consume, read, or inhibitor behavior.
    patterns
        Nonempty ordered pattern demand. Consume/read modes require binding
        ``CpnTokenPattern`` members. Inhibitor mode requires nonbinding
        ``CpnInhibitorPattern`` members because successful absence
        cannot produce a variable value. Order and duplicates are meaningful.

    Raises
    ------
    TypeError
        The mode, tuple, or pattern variant has the wrong semantic type.
    ValueError
        The pattern tuple is empty.
    """

    mode: CpnInputMode
    patterns: tuple[CpnTokenPattern | CpnInhibitorPattern, ...]

    def __post_init__(self) -> None:
        """Validate exact mode and immutable nonempty pattern demand."""
        if not isinstance(self.mode, CpnInputMode):
            raise TypeError("mode must be CpnInputMode")
        if type(self.patterns) is not tuple:
            raise TypeError("patterns must be a tuple")
        if not self.patterns:
            raise ValueError("patterns must not be empty")
        expected_type = (
            CpnInhibitorPattern
            if self.mode is CpnInputMode.INHIBIT
            else CpnTokenPattern
        )
        if any(type(item) is not expected_type for item in self.patterns):
            raise TypeError(
                f"{self.mode.value} patterns must be {expected_type.__name__}"
            )


@dataclass(frozen=True, slots=True)
class CpnTokenTemplate:
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

    color_identity: CpnColorIdentity
    value_expression: CpnValueExpression
    token_identity_expression: CpnValueExpression | None = None

    def __post_init__(self) -> None:
        """Validate exact nominal template components."""
        if type(self.color_identity) is not CpnColorIdentity:
            raise TypeError("color_identity must be CpnColorIdentity")
        if type(self.value_expression) is not CpnValueExpression:
            raise TypeError("value_expression must be CpnValueExpression")
        if self.token_identity_expression is not None and (
            type(self.token_identity_expression) is not CpnValueExpression
        ):
            raise TypeError(
                "token_identity_expression must be CpnValueExpression or None"
            )


@dataclass(frozen=True, slots=True)
class CpnOutputInscription:
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

    templates: tuple[CpnTokenTemplate, ...]

    def __post_init__(self) -> None:
        """Require an immutable nonempty ordered template tuple."""
        if type(self.templates) is not tuple or any(
            type(item) is not CpnTokenTemplate for item in self.templates
        ):
            raise TypeError("templates must be a tuple of CpnTokenTemplate")
        if not self.templates:
            raise ValueError("templates must not be empty")


@dataclass(frozen=True, slots=True)
class CpnGuardEvaluationResult:
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
