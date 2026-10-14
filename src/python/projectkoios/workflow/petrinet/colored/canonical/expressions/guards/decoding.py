"""Canonical guard-expression transport."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ....expressions.grammar import (
    CpnGuardExpression,
    CpnGuardOperator,
)
from ....values import (
    CpnControlRecordTypeDefinition,
)
from ...json import CpnCanonicalJsonParser, CpnCanonicalJsonParsingInput
from ..errors import (
    CpnExpressionCanonicalCodecError,
    CpnExpressionCanonicalCodecErrorCode,
)
from ..values.decoding import (
    CpnValueExpressionCanonicalDecoder,
    CpnValueExpressionCanonicalDecodingInput,
)


@dataclass(frozen=True, slots=True)
class CpnGuardCanonicalDecoderIdentity:
    """Identity of exact guard reconstruction semantics."""

    value: str = "projectkoios.workflow.cpn.guard-decoder:0.1"


@dataclass(frozen=True, slots=True)
class CpnGuardCanonicalDecodingInput:
    """Exact canonical guard bytes and retained record schemas."""

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
class CpnGuardCanonicalDecodingResult:
    """One reconstructed bounded guard."""

    guard: CpnGuardExpression


@final
class CpnGuardCanonicalDecoder:
    """Directly reconstruct one bounded tagged guard tree."""

    __slots__ = ()

    @property
    def identity(self) -> CpnGuardCanonicalDecoderIdentity:
        """Return exact guard decoding semantics identity."""
        return CpnGuardCanonicalDecoderIdentity()

    def execute(
        self, decoding_input: CpnGuardCanonicalDecodingInput
    ) -> CpnGuardCanonicalDecodingResult:
        """Reconstruct nested guards and exact value expressions."""
        if type(decoding_input) is not CpnGuardCanonicalDecodingInput:
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnGuardCanonicalDecodingInput",
            )
        state_root = json.loads(
            CpnCanonicalJsonParser()
            .execute(
                CpnCanonicalJsonParsingInput(decoding_input.canonical_bytes)
            )
            .canonical_bytes
        )
        guards: dict[int, CpnGuardExpression] = {}
        stack: list[tuple[object, tuple[str, ...], bool, int]] = [
            (state_root, (), False, 0)
        ]
        nodes = 0
        while stack:
            state, path, ready, depth = stack.pop()
            if (
                type(state) is not list
                or len(state) != 4
                or type(state[0]) is not str
                or type(state[1]) is not list
            ):
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.INVALID_SHAPE,
                    path,
                    "guard must contain operator, nested, left, and right",
                )
            nodes += 1 if not ready else 0
            if nodes > 4096 or depth > 64:
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.BOUND_EXCEEDED,
                    path,
                    "guard exceeds 4096 nodes or depth 64",
                )
            if not ready:
                stack.append((state, path, True, depth))
                for index in range(len(state[1]) - 1, -1, -1):
                    stack.append(
                        (
                            state[1][index],
                            path + ("nested", str(index)),
                            False,
                            depth + 1,
                        )
                    )
                continue
            try:
                operator = CpnGuardOperator(state[0])
                left = (
                    CpnValueExpressionCanonicalDecoder()
                    .execute(
                        CpnValueExpressionCanonicalDecodingInput(
                            json.dumps(
                                state[2],
                                ensure_ascii=False,
                                allow_nan=False,
                                separators=(",", ":"),
                            ).encode("utf-8"),
                            decoding_input.type_definitions,
                        )
                    )
                    .expression
                    if state[2] is not None
                    else None
                )
                right = (
                    CpnValueExpressionCanonicalDecoder()
                    .execute(
                        CpnValueExpressionCanonicalDecodingInput(
                            json.dumps(
                                state[3],
                                ensure_ascii=False,
                                allow_nan=False,
                                separators=(",", ":"),
                            ).encode("utf-8"),
                            decoding_input.type_definitions,
                        )
                    )
                    .expression
                    if state[3] is not None
                    else None
                )
                guard = CpnGuardExpression(
                    operator,
                    tuple(guards[id(item)] for item in state[1]),
                    left,
                    right,
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise CpnExpressionCanonicalCodecError(
                    CpnExpressionCanonicalCodecErrorCode.INVALID_EXPRESSION,
                    path,
                    "guard violates its exact tagged representation",
                ) from exc
            guards[id(state)] = guard
        return CpnGuardCanonicalDecodingResult(guards[id(state_root)])
