"""Deterministic ordering for admitted generic CPN values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ...values import (
    CpnControlRecord,
    CpnValue,
    CpnValueKind,
)


@dataclass(frozen=True, slots=True)
class CpnValueOrderingPolicyIdentity:
    """Identity of exact recursive generic-value ordering semantics."""

    value: str = "projectkoios.workflow.cpn.value-ordering-policy:0.1"

    def __post_init__(self) -> None:
        if type(self.value) is not str or not self.value:
            raise TypeError("ordering identity must be a nonempty string")


@dataclass(frozen=True, slots=True)
class CpnValueOrderingInput:
    """One exact generic value to project into its ordering key."""

    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@dataclass(frozen=True, slots=True)
class CpnValueOrderingResult:
    """One immutable recursively comparable generic-value key."""

    key: tuple[object, ...]

    def __post_init__(self) -> None:
        if type(self.key) is not tuple:
            raise TypeError("key must be a tuple")


@final
class CpnValueOrderingPolicy:
    """Directly derive deterministic ordering for scalar and record values."""

    __slots__ = ()

    @property
    def identity(self) -> CpnValueOrderingPolicyIdentity:
        """Return the exact ordering semantics identity."""
        return CpnValueOrderingPolicyIdentity()

    def execute(
        self, ordering_input: CpnValueOrderingInput
    ) -> CpnValueOrderingResult:
        """Return the recursive key without invoking owner or provider code."""
        if type(ordering_input) is not CpnValueOrderingInput:
            raise TypeError("ordering_input must be CpnValueOrderingInput")
        root = ordering_input.value
        keys: dict[int, tuple[object, ...]] = {}
        stack: list[tuple[CpnValue, bool, frozenset[int], int]] = [
            (root, False, frozenset(), 1)
        ]
        nodes = 0
        while stack:
            value, ready, ancestors, record_depth = stack.pop()
            if not ready:
                nodes += 1
                if nodes > 256:
                    raise ValueError("control-record value exceeds 256 nodes")
            if value.kind is CpnValueKind.CONTROL_RECORD and not ready:
                if record_depth > 8:
                    raise ValueError("control-record nesting exceeds depth 8")
                assert type(value.value) is CpnControlRecord
                marker = id(value.value)
                if marker in ancestors:
                    raise ValueError("cyclic control-record value")
                stack.append((value, True, ancestors, record_depth))
                for field in reversed(value.value.fields):
                    stack.append(
                        (
                            field.value,
                            False,
                            ancestors | {marker},
                            record_depth
                            + (
                                1
                                if field.value.kind
                                is CpnValueKind.CONTROL_RECORD
                                else 0
                            ),
                        )
                    )
                continue
            if value.kind is CpnValueKind.NONE:
                active: object = ()
            elif value.kind is CpnValueKind.CONTROL_RECORD:
                assert type(value.value) is CpnControlRecord
                active = (
                    value.value.type_identity.value,
                    tuple(
                        (field.identity.value, keys[id(field.value)])
                        for field in value.value.fields
                    ),
                )
            elif value.kind is CpnValueKind.STRING_SEQUENCE:
                assert type(value.value) is tuple
                active = value.value
            else:
                active = value.value
            keys[id(value)] = (value.kind.value, active)
        return CpnValueOrderingResult(keys[id(root)])
