"""Canonical guard-expression transport."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ....expressions.collection.guards import (
    CpnGuardExpressionCollectionInput,
    CpnGuardExpressionCollector,
)
from ....expressions.errors import CpnExpressionOperationError
from ....expressions.grammar import (
    CpnGuardExpression,
)
from ....values import (
    CpnControlRecordTypeDefinition,
)
from ..errors import (
    CpnExpressionCanonicalCodecError,
    CpnExpressionCanonicalCodecErrorCode,
)
from ..values.canonicalization import (
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
