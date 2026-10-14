"""Canonical tagged CPN value projection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ....values import CpnControlRecord, CpnValue, CpnValueKind


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalizerIdentity:
    """Identity of exact JSON-safe tagged-value projection semantics."""

    value: str = "projectkoios.workflow.cpn.value-canonicalizer:0.1"


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalizationInput:
    """One exact generic value to project into canonical state."""

    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalizationResult:
    """Exact immutable canonical bytes for one active value."""

    canonical_bytes: bytes

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")


@final
class CpnValueCanonicalizer:
    """Directly project scalar and record values without owner callbacks."""

    __slots__ = ()

    @property
    def identity(self) -> CpnValueCanonicalizerIdentity:
        """Return the exact canonical projection identity."""
        return CpnValueCanonicalizerIdentity()

    def execute(
        self, canonicalization_input: CpnValueCanonicalizationInput
    ) -> CpnValueCanonicalizationResult:
        """Return an immutable canonical state using explicit scalar tags."""
        if type(canonicalization_input) is not CpnValueCanonicalizationInput:
            raise TypeError(
                "canonicalization_input must be CpnValueCanonicalizationInput"
            )
        root = canonicalization_input.value
        states: dict[int, object] = {}
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
            active: object
            if value.kind is CpnValueKind.INTEGER:
                active = str(value.value)
            elif value.kind is CpnValueKind.REAL:
                assert type(value.value) is float
                active = value.value.hex()
            elif value.kind is CpnValueKind.STRING_SEQUENCE:
                assert type(value.value) is tuple
                active = tuple(value.value)
            elif value.kind is CpnValueKind.CONTROL_RECORD:
                assert type(value.value) is CpnControlRecord
                active = (
                    "control_record",
                    value.value.type_identity.value,
                    tuple(
                        (
                            field.identity.value,
                            field.value.kind.value,
                            states[id(field.value)],
                        )
                        for field in value.value.fields
                    ),
                )
            else:
                assert value.value is None or type(value.value) in (bool, str)
                active = value.value
            states[id(value)] = active
        return CpnValueCanonicalizationResult(
            json.dumps(
                states[id(root)],
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
