"""Deterministic ordering of complete enabled-binding sets."""

from __future__ import annotations
from dataclasses import dataclass
from typing import final
from ..canonical.bindings import (
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingEncodingInput,
)
from ..control.records.ordering import (
    CpnValueOrderingInput,
    CpnValueOrderingPolicy,
)
from ..definitions import CpnDefinition
from ..bindings import CpnBinding
from .results.definition import CpnOrderingPolicyIdentity


@dataclass(frozen=True, slots=True)
class CpnEnabledBindingOrderingInput:
    """One exact definition and unique binding set requested for ordering."""

    definition: CpnDefinition
    bindings: frozenset[CpnBinding]

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.bindings) is not frozenset or any(
            type(item) is not CpnBinding for item in self.bindings
        ):
            raise TypeError("bindings must contain exact CpnBinding values")


@dataclass(frozen=True, slots=True)
class CpnEnabledBindingOrderingResult:
    """One deterministically ordered complete binding tuple."""

    bindings: tuple[CpnBinding, ...]

    def __post_init__(self) -> None:
        if type(self.bindings) is not tuple or any(
            type(item) is not CpnBinding for item in self.bindings
        ):
            raise TypeError("bindings must contain exact CpnBinding values")
        if len(set(self.bindings)) != len(self.bindings):
            raise ValueError("bindings must be unique")


@final
class CpnEnabledBindingOrderingPolicy:
    """Order enabled bindings by transition priority and generic values."""

    __slots__ = ()

    @property
    def identity(self) -> CpnOrderingPolicyIdentity:
        """Return exact enabled-binding ordering semantics identity."""
        return CpnOrderingPolicyIdentity(
            "colored-petri-net-enablement-order-v1"
        )

    def execute(
        self, ordering_input: CpnEnabledBindingOrderingInput
    ) -> CpnEnabledBindingOrderingResult:
        """Return all supplied bindings in the exact execution order."""
        if type(ordering_input) is not CpnEnabledBindingOrderingInput:
            raise TypeError(
                "ordering_input must be CpnEnabledBindingOrderingInput"
            )
        priority = {
            identity: position
            for position, identity in enumerate(
                ordering_input.definition.transition_priority
            )
        }
        if any(
            item.transition_identity not in priority
            for item in ordering_input.bindings
        ):
            raise ValueError("binding names an unordered transition")
        ordered: list[tuple[tuple[object, ...], bytes, CpnBinding]] = []
        for binding in ordering_input.bindings:
            key = (
                priority[binding.transition_identity],
                tuple(
                    CpnValueOrderingPolicy()
                    .execute(CpnValueOrderingInput(item.value))
                    .key
                    for item in binding.assignments
                ),
            )
            canonical_bytes = (
                CpnCanonicalBindingCodec()
                .encode(CpnCanonicalBindingEncodingInput(binding))
                .canonical_bytes
            )
            ordered.append((key, canonical_bytes, binding))
        ordered.sort()
        return CpnEnabledBindingOrderingResult(
            tuple(item[2] for item in ordered)
        )
