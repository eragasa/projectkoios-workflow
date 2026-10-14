"""Typed content-identified transition execution routes."""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256

from ..definitions import CpnDefinitionIdentity, CpnTransitionIdentity
from ..mappings.values import WorkflowValueMappingDescriptor


class WorkflowTransitionRouteKind(StrEnum):
    """Closed execution-plan transition route alternatives."""

    PURE_CPN = "pure_cpn"
    OWNER_ADAPTER = "owner_adapter"
    PROTECTED_EFFECT = "protected_effect"
    HIERARCHICAL_CHILD = "hierarchical_child"


@dataclass(frozen=True, slots=True)
class WorkflowTransitionRoute:
    """One exact transition route without provider or deployment selection."""

    definition_identity: CpnDefinitionIdentity
    transition_identity: CpnTransitionIdentity
    kind: WorkflowTransitionRouteKind
    mapping_descriptors: tuple[WorkflowValueMappingDescriptor, ...]
    protected_effect_capability_identity: str | None
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.definition_identity) is not CpnDefinitionIdentity:
            raise TypeError("definition_identity must be CpnDefinitionIdentity")
        if type(self.transition_identity) is not CpnTransitionIdentity:
            raise TypeError("transition_identity must be CpnTransitionIdentity")
        if not isinstance(self.kind, WorkflowTransitionRouteKind):
            raise TypeError("kind must be WorkflowTransitionRouteKind")
        mappings = self.mapping_descriptors
        if type(mappings) is not tuple or any(
            type(item) is not WorkflowValueMappingDescriptor
            for item in mappings
        ):
            raise TypeError(
                "mapping_descriptors must contain exact WorkflowValueMappingDescriptor records"
            )
        mapping_identities = tuple(item.identity for item in mappings)
        if mapping_identities != tuple(sorted(set(mapping_identities))):
            raise ValueError(
                "mapping_descriptors must be unique and identity-ordered"
            )
        capability = self.protected_effect_capability_identity
        if capability is not None and (
            type(capability) is not str or not capability
        ):
            raise TypeError(
                "protected_effect_capability_identity must be a nonempty string or None"
            )
        if self.kind is WorkflowTransitionRouteKind.PURE_CPN and (
            mappings or capability is not None
        ):
            raise ValueError(
                "pure CPN routes must not declare mappings or protected effects"
            )
        if self.kind is WorkflowTransitionRouteKind.OWNER_ADAPTER and (
            not mappings or capability is not None
        ):
            raise ValueError(
                "owner-adapter routes require mappings and no protected effect"
            )
        if self.kind is WorkflowTransitionRouteKind.PROTECTED_EFFECT and (
            not mappings or capability is None
        ):
            raise ValueError(
                "protected-effect routes require mappings and one capability"
            )
        if self.kind is WorkflowTransitionRouteKind.HIERARCHICAL_CHILD and (
            mappings or capability is not None
        ):
            raise ValueError(
                "hierarchical routes obtain mappings from their child binding"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "contract_version": str(self.contract_version),
            "definition_identity": self.definition_identity.value,
            "kind": self.kind.value,
            "mapping_descriptor_identities": list(mapping_identities),
            "protected_effect_capability_identity": capability,
            "transition_identity": self.transition_identity.value,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.transition-route:0.1:"
            + sha256(encoded).hexdigest(),
        )
