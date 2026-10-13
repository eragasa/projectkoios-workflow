"""Canonical value-expression transport."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ....control.records.values.canonicalization import (
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ....expressions.grammar import (
    CpnValueExpression,
    CpnValueExpressionKind,
)
from ....expressions.validation.structure import (
    CpnExpressionStructureValidationInput,
    CpnExpressionStructureValidator,
)
from ....values import (
    CpnControlRecordTypeDefinition,
)
from ..errors import (
    CpnExpressionCanonicalCodecError,
    CpnExpressionCanonicalCodecErrorCode,
)


@dataclass(frozen=True, slots=True)
class CpnValueExpressionCanonicalizerIdentity:
    """Identity of exact value-expression canonicalization semantics."""

    value: str = "projectkoios.workflow.cpn.value-expression-canonicalizer:0.1"


@dataclass(frozen=True, slots=True)
class CpnValueExpressionCanonicalizationInput:
    """One closed expression and its retained record schemas."""

    expression: CpnValueExpression
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...] = ()


@dataclass(frozen=True, slots=True)
class CpnValueExpressionCanonicalizationResult:
    """Exact immutable canonical bytes for one value expression."""

    canonical_bytes: bytes

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")


@final
class CpnValueExpressionCanonicalizer:
    """Directly canonicalize every closed value-expression node."""

    __slots__ = ()

    @property
    def identity(self) -> CpnValueExpressionCanonicalizerIdentity:
        """Return exact canonicalization semantics identity."""
        return CpnValueExpressionCanonicalizerIdentity()

    def execute(
        self, canonicalization_input: CpnValueExpressionCanonicalizationInput
    ) -> CpnValueExpressionCanonicalizationResult:
        """Validate then produce the exact tagged JSON-safe expression state."""
        if (
            type(canonicalization_input)
            is not CpnValueExpressionCanonicalizationInput
        ):
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnValueExpressionCanonicalizationInput",
            )
        validation = CpnExpressionStructureValidator().execute(
            CpnExpressionStructureValidationInput(
                canonicalization_input.expression,
                canonicalization_input.type_definitions,
            )
        )
        if not validation.is_valid:
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.INVALID_EXPRESSION,
                validation.issues[0].path,
                validation.issues[0].code.value,
            )
        states: dict[int, object] = {}
        stack: list[tuple[CpnValueExpression, bool]] = [
            (canonicalization_input.expression, False)
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
                value_state = json.loads(
                    CpnValueCanonicalizer()
                    .execute(CpnValueCanonicalizationInput(expression.literal))
                    .canonical_bytes
                )
                state: object = [
                    expression.kind.value,
                    expression.literal.kind.value,
                    value_state,
                ]
            elif expression.kind is CpnValueExpressionKind.VARIABLE:
                assert expression.variable_identity is not None
                state = [
                    expression.kind.value,
                    expression.variable_identity.value,
                ]
            elif expression.kind is (CpnValueExpressionKind.FIELD_PROJECTION):
                assert expression.base_expression is not None
                state = [
                    expression.kind.value,
                    states[id(expression.base_expression)],
                    [item.value for item in expression.field_path],
                ]
            else:
                assert expression.record_type_identity is not None
                state = [
                    expression.kind.value,
                    expression.record_type_identity.value,
                    [
                        [field.identity.value, states[id(field.expression)]]
                        for field in expression.constructor_fields
                    ],
                ]
            states[id(expression)] = state
        return CpnValueExpressionCanonicalizationResult(
            json.dumps(
                states[id(canonicalization_input.expression)],
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
