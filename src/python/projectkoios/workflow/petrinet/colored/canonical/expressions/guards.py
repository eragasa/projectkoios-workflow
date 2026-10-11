"""Canonical guard-expression transport."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ...expressions.collection import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
)
from ...expressions.errors import CpnExpressionOperationError
from ...expressions.grammar import (
    CpnGuardExpression,
    CpnGuardOperator,
)
from ...values import (
    CpnControlRecordTypeDefinition,
)
from ..json import CpnCanonicalJsonParser, CpnCanonicalJsonParsingInput
from .errors import (
    CpnExpressionCanonicalCodecError,
    CpnExpressionCanonicalCodecErrorCode,
)
from .values import (
    CpnValueExpressionCanonicalDecoder,
    CpnValueExpressionCanonicalDecodingInput,
    CpnValueExpressionCanonicalizationInput,
    CpnValueExpressionCanonicalizer,
)


@dataclass(frozen=True, slots=True)
class CpnGuardCanonicalizerIdentity:
    """Identity of exact guard canonicalization semantics."""

    value: str = "projectkoios.workflow.cpn.guard-canonicalizer:0.1"


@dataclass(frozen=True, slots=True)
class CpnGuardCanonicalizationInput:
    """One guard and its retained record schemas."""

    guard: CpnGuardExpression
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...] = ()


@dataclass(frozen=True, slots=True)
class CpnGuardCanonicalizationResult:
    """Exact immutable canonical bytes for one guard tree."""

    canonical_bytes: bytes


@final
class CpnGuardCanonicalizer:
    """Directly canonicalize one bounded closed guard tree."""

    __slots__ = ()

    @property
    def identity(self) -> CpnGuardCanonicalizerIdentity:
        """Return exact guard canonicalization semantics identity."""
        return CpnGuardCanonicalizerIdentity()

    def execute(
        self, canonicalization_input: CpnGuardCanonicalizationInput
    ) -> CpnGuardCanonicalizationResult:
        """Canonicalize nested guards and referenced value expressions."""
        if type(canonicalization_input) is not CpnGuardCanonicalizationInput:
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnGuardCanonicalizationInput",
            )
        try:
            CpnGuardExpressionCollector().execute(
                CpnGuardExpressionCollectionInput(canonicalization_input.guard)
            )
        except CpnExpressionOperationError as exc:
            raise CpnExpressionCanonicalCodecError(
                CpnExpressionCanonicalCodecErrorCode.BOUND_EXCEEDED,
                exc.path,
                exc.code.value,
            ) from exc
        states: dict[int, object] = {}
        stack: list[tuple[CpnGuardExpression, bool]] = [
            (canonicalization_input.guard, False)
        ]
        while stack:
            guard, ready = stack.pop()
            if not ready:
                stack.append((guard, True))
                for nested in reversed(guard.operands):
                    stack.append((nested, False))
                continue
            left = (
                CpnValueExpressionCanonicalizer()
                .execute(
                    CpnValueExpressionCanonicalizationInput(
                        guard.left, canonicalization_input.type_definitions
                    )
                )
                .canonical_bytes
                if guard.left is not None
                else None
            )
            right = (
                CpnValueExpressionCanonicalizer()
                .execute(
                    CpnValueExpressionCanonicalizationInput(
                        guard.right, canonicalization_input.type_definitions
                    )
                )
                .canonical_bytes
                if guard.right is not None
                else None
            )
            states[id(guard)] = [
                guard.operator.value,
                [states[id(nested)] for nested in guard.operands],
                None if left is None else json.loads(left),
                None if right is None else json.loads(right),
            ]
        return CpnGuardCanonicalizationResult(
            json.dumps(
                states[id(canonicalization_input.guard)],
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
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
