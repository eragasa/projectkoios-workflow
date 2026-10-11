"""Canonical value-expression transport."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ...control.records.value_canonical import (
    CpnValueCanonicalDecodingInput,
    CpnValueCanonicalDecoder,
    CpnValueCanonicalizationInput,
    CpnValueCanonicalizer,
)
from ...expressions.grammar import (
    CpnControlRecordConstructorField,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from ...expressions.validation import (
    CpnExpressionStructureValidationInput,
    CpnExpressionStructureValidator,
)
from ...expressions.grammar import CpnBindingVariableIdentity
from ...values import (
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
)
from ..json import (
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)
from .errors import (
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


@dataclass(frozen=True, slots=True)
class CpnValueExpressionCanonicalDecoderIdentity:
    """Identity of exact value-expression reconstruction semantics."""

    value: str = "projectkoios.workflow.cpn.value-expression-decoder:0.1"


@dataclass(frozen=True, slots=True)
class CpnValueExpressionCanonicalDecodingInput:
    """Exact canonical expression bytes and retained record schemas."""

    canonical_bytes: bytes
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must contain exact control-record definitions"
            )


@dataclass(frozen=True, slots=True)
class CpnValueExpressionCanonicalDecodingResult:
    """One reconstructed closed value expression."""

    expression: CpnValueExpression


@final
class CpnValueExpressionCanonicalDecoder:
    """Directly reconstruct a bounded tagged value expression."""

    __slots__ = ()

    @property
    def identity(self) -> CpnValueExpressionCanonicalDecoderIdentity:
        """Return exact decoding semantics identity."""
        return CpnValueExpressionCanonicalDecoderIdentity()

    def execute(
        self, decoding_input: CpnValueExpressionCanonicalDecodingInput
    ) -> CpnValueExpressionCanonicalDecodingResult:
        """Reconstruct then independently validate one expression graph."""
        if type(decoding_input) is not CpnValueExpressionCanonicalDecodingInput:
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnValueExpressionCanonicalDecodingInput",
            )
        state_root = json.loads(
            CpnCanonicalJsonParser()
            .execute(
                CpnCanonicalJsonParsingInput(decoding_input.canonical_bytes)
            )
            .canonical_bytes
        )
        expressions: dict[int, CpnValueExpression] = {}
        stack: list[tuple[object, tuple[str, ...], bool, int]] = [
            (state_root, (), False, 0)
        ]
        nodes = 0
        while stack:
            state, path, ready, depth = stack.pop()
            if (
                type(state) is not list
                or not state
                or type(state[0]) is not str
            ):
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.INVALID_SHAPE,
                    path,
                    "expression must be a nonempty tagged array",
                )
            nodes += 1 if not ready else 0
            if nodes > 4096 or depth > 64:
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.BOUND_EXCEEDED,
                    path,
                    "expression exceeds 4096 nodes or depth 64",
                )
            try:
                kind = CpnValueExpressionKind(state[0])
            except ValueError as exc:
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.INVALID_SHAPE,
                    path + ("kind",),
                    "unsupported expression tag",
                ) from exc
            if not ready:
                stack.append((state, path, True, depth))
                if kind is CpnValueExpressionKind.FIELD_PROJECTION:
                    if len(state) != 3:
                        raise CpnExpressionCanonicalCodecError(
                            CpnExpressionCanonicalCodecErrorCode.INVALID_SHAPE,
                            path,
                            "projection must contain tag, base, and field path",
                        )
                    stack.append((state[1], path + ("base",), False, depth + 1))
                elif kind is (
                    CpnValueExpressionKind.CONTROL_RECORD_CONSTRUCTOR
                ):
                    if len(state) != 3 or type(state[2]) is not list:
                        raise CpnExpressionCanonicalCodecError(
                            CpnExpressionCanonicalCodecErrorCode.INVALID_SHAPE,
                            path,
                            "constructor must contain tag, type, and fields",
                        )
                    for index in range(len(state[2]) - 1, -1, -1):
                        field = state[2][index]
                        if (
                            type(field) is not list
                            or len(field) != 2
                            or type(field[0]) is not str
                        ):
                            raise CpnExpressionCanonicalCodecError(
                                CpnExpressionCanonicalCodecErrorCode.INVALID_SHAPE,
                                path + ("fields", str(index)),
                                "constructor field must contain identity and expression",
                            )
                        stack.append(
                            (
                                field[1],
                                path + ("fields", str(index), "expression"),
                                False,
                                depth + 1,
                            )
                        )
                continue
            try:
                if kind is CpnValueExpressionKind.LITERAL:
                    if len(state) != 3 or type(state[1]) is not str:
                        raise TypeError("literal shape")
                    literal = (
                        CpnValueCanonicalDecoder()
                        .execute(
                            CpnValueCanonicalDecodingInput(
                                state[1],
                                json.dumps(
                                    state[2],
                                    ensure_ascii=False,
                                    allow_nan=False,
                                    separators=(",", ":"),
                                ).encode("utf-8"),
                                decoding_input.type_definitions,
                            )
                        )
                        .value
                    )
                    expression = CpnValueExpression(kind, literal=literal)
                elif kind is CpnValueExpressionKind.VARIABLE:
                    if len(state) != 2 or type(state[1]) is not str:
                        raise TypeError("variable shape")
                    expression = CpnValueExpression(
                        kind,
                        variable_identity=CpnBindingVariableIdentity(state[1]),
                    )
                elif kind is (CpnValueExpressionKind.FIELD_PROJECTION):
                    if type(state[2]) is not list or any(
                        type(item) is not str for item in state[2]
                    ):
                        raise TypeError("field path shape")
                    expression = CpnValueExpression(
                        kind,
                        base_expression=expressions[id(state[1])],
                        field_path=tuple(
                            CpnControlRecordFieldIdentity(item)
                            for item in state[2]
                        ),
                    )
                else:
                    if type(state[1]) is not str:
                        raise TypeError("record type shape")
                    fields = tuple(
                        CpnControlRecordConstructorField(
                            CpnControlRecordFieldIdentity(field[0]),
                            expressions[id(field[1])],
                        )
                        for field in state[2]
                    )
                    expression = CpnValueExpression(
                        kind,
                        record_type_identity=CpnControlRecordTypeIdentity(
                            state[1]
                        ),
                        constructor_fields=fields,
                    )
            except (
                KeyError,
                OverflowError,
                TypeError,
                UnicodeError,
                ValueError,
            ) as exc:
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.INVALID_EXPRESSION,
                    path,
                    "expression violates its tagged representation",
                ) from exc
            expressions[id(state)] = expression
        expression = expressions[id(state_root)]
        validation = CpnExpressionStructureValidator().execute(
            CpnExpressionStructureValidationInput(
                expression, decoding_input.type_definitions
            )
        )
        if not validation.is_valid:
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.INVALID_EXPRESSION,
                validation.issues[0].path,
                validation.issues[0].code.value,
            )
        return CpnValueExpressionCanonicalDecodingResult(expression)
