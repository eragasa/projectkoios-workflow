"""Typed parent-to-child hierarchical execution-plan bindings."""

import json
from dataclasses import dataclass, field
from hashlib import sha256

from ..definitions import CpnDefinitionIdentity, CpnPlaceIdentity
from ..mappings.values import WorkflowValueMappingDescriptor
from ..plans.identities import WorkflowExecutionPlanIdentity
from ..routes.transitions import (
    WorkflowTransitionRoute,
    WorkflowTransitionRouteKind,
)
from ..values import CpnColorIdentity
from .exports.definition import WorkflowChildDefinitionExportIdentity
from .interfaces import WorkflowTerminalDeliveryRequirement

_MAX_SIGNED_64 = 9_223_372_036_854_775_807


@dataclass(frozen=True, slots=True)
class WorkflowHierarchicalChildInputMapping:
    """Exact parent place/color to child input-port mapping."""

    parent_place_identity: CpnPlaceIdentity
    parent_color_identity: CpnColorIdentity
    child_input_port_identity: str
    mapping_descriptor: WorkflowValueMappingDescriptor
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.parent_place_identity) is not CpnPlaceIdentity:
            raise TypeError("parent_place_identity must be CpnPlaceIdentity")
        if type(self.parent_color_identity) is not CpnColorIdentity:
            raise TypeError("parent_color_identity must be CpnColorIdentity")
        if (
            type(self.child_input_port_identity) is not str
            or not self.child_input_port_identity
        ):
            raise TypeError(
                "child_input_port_identity must be a nonempty string"
            )
        if type(self.mapping_descriptor) is not WorkflowValueMappingDescriptor:
            raise TypeError(
                "mapping_descriptor must be WorkflowValueMappingDescriptor"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "child_input_port_identity": self.child_input_port_identity,
            "contract_version": str(self.contract_version),
            "mapping_descriptor_identity": self.mapping_descriptor.identity,
            "parent_color_identity": self.parent_color_identity.value,
            "parent_place_identity": self.parent_place_identity.value,
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
            "projectkoios.workflow.hierarchical-child-input-mapping:0.1:"
            + sha256(encoded).hexdigest(),
        )


@dataclass(frozen=True, slots=True)
class WorkflowHierarchicalChildTerminalMapping:
    """Exact child terminal requirement to parent external-output mapping."""

    terminal_delivery_requirement: WorkflowTerminalDeliveryRequirement
    parent_external_output_mapping_descriptor: WorkflowValueMappingDescriptor
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if (
            type(self.terminal_delivery_requirement)
            is not WorkflowTerminalDeliveryRequirement
        ):
            raise TypeError(
                "terminal_delivery_requirement must be WorkflowTerminalDeliveryRequirement"
            )
        if (
            type(self.parent_external_output_mapping_descriptor)
            is not WorkflowValueMappingDescriptor
        ):
            raise TypeError(
                "parent_external_output_mapping_descriptor must be WorkflowValueMappingDescriptor"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "contract_version": str(self.contract_version),
            "parent_external_output_mapping_descriptor_identity": (
                self.parent_external_output_mapping_descriptor.identity
            ),
            "terminal_classification_identity": (
                self.terminal_delivery_requirement.terminal_classification_identity
            ),
            "terminal_delivery_requirement_identity": (
                self.terminal_delivery_requirement.identity
            ),
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
            "projectkoios.workflow.hierarchical-child-terminal-mapping:0.1:"
            + sha256(encoded).hexdigest(),
        )


@dataclass(frozen=True, slots=True)
class WorkflowHierarchicalChildBinding:
    """Complete v0.1 binding to one separately authoritative child plan."""

    parent_definition_identity: CpnDefinitionIdentity
    transition_route: WorkflowTransitionRoute
    child_export_identity: WorkflowChildDefinitionExportIdentity
    child_execution_plan_identity: WorkflowExecutionPlanIdentity
    input_mapping: WorkflowHierarchicalChildInputMapping
    terminal_mappings: tuple[WorkflowHierarchicalChildTerminalMapping, ...]
    child_instance_cardinality: int
    child_ordinal: int
    cancellation_propagation_policy_identity: str
    quiescence_required: bool
    maximum_correlation_field_count: int
    maximum_external_output_reference_count: int
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.parent_definition_identity) is not CpnDefinitionIdentity:
            raise TypeError(
                "parent_definition_identity must be CpnDefinitionIdentity"
            )
        if type(self.transition_route) is not WorkflowTransitionRoute:
            raise TypeError("transition_route must be WorkflowTransitionRoute")
        if (
            self.transition_route.kind
            is not WorkflowTransitionRouteKind.HIERARCHICAL_CHILD
        ):
            raise ValueError(
                "child binding requires a hierarchical transition route"
            )
        if (
            self.transition_route.definition_identity
            != self.parent_definition_identity
        ):
            raise ValueError("transition route must name the parent definition")
        if (
            type(self.child_export_identity)
            is not WorkflowChildDefinitionExportIdentity
        ):
            raise TypeError(
                "child_export_identity must be WorkflowChildDefinitionExportIdentity"
            )
        if (
            type(self.child_execution_plan_identity)
            is not WorkflowExecutionPlanIdentity
        ):
            raise TypeError(
                "child_execution_plan_identity must be WorkflowExecutionPlanIdentity"
            )
        if (
            type(self.input_mapping)
            is not WorkflowHierarchicalChildInputMapping
        ):
            raise TypeError(
                "input_mapping must be WorkflowHierarchicalChildInputMapping"
            )
        mappings = self.terminal_mappings
        if type(mappings) is not tuple or any(
            type(item) is not WorkflowHierarchicalChildTerminalMapping
            for item in mappings
        ):
            raise TypeError(
                "terminal_mappings must contain exact child terminal mappings"
            )
        if not mappings:
            raise ValueError("terminal_mappings must not be empty")
        classifications = tuple(
            item.terminal_delivery_requirement.terminal_classification_identity
            for item in mappings
        )
        if classifications != tuple(sorted(set(classifications))):
            raise ValueError(
                "terminal_mappings must be unique and classification-ordered"
            )
        if self.child_instance_cardinality != 1:
            raise ValueError(
                "contract v0.1 requires child_instance_cardinality 1"
            )
        if self.child_ordinal != 0:
            raise ValueError("contract v0.1 requires child_ordinal 0")
        if (
            type(self.cancellation_propagation_policy_identity) is not str
            or not self.cancellation_propagation_policy_identity
        ):
            raise TypeError(
                "cancellation_propagation_policy_identity must be a nonempty string"
            )
        if type(self.quiescence_required) is not bool:
            raise TypeError("quiescence_required must be bool")
        for name in (
            "maximum_correlation_field_count",
            "maximum_external_output_reference_count",
            "contract_version",
        ):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= _MAX_SIGNED_64:
                raise ValueError(
                    f"{name} must be a positive signed 64-bit integer"
                )
        state = {
            "cancellation_propagation_policy_identity": (
                self.cancellation_propagation_policy_identity
            ),
            "child_execution_plan_identity": self.child_execution_plan_identity.value,
            "child_export_identity": self.child_export_identity.value,
            "child_instance_cardinality": str(self.child_instance_cardinality),
            "child_ordinal": str(self.child_ordinal),
            "contract_version": str(self.contract_version),
            "input_mapping_identity": self.input_mapping.identity,
            "maximum_correlation_field_count": str(
                self.maximum_correlation_field_count
            ),
            "maximum_external_output_reference_count": str(
                self.maximum_external_output_reference_count
            ),
            "parent_definition_identity": self.parent_definition_identity.value,
            "quiescence_required": self.quiescence_required,
            "terminal_mapping_identities": [item.identity for item in mappings],
            "transition_route_identity": self.transition_route.identity,
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
            "projectkoios.workflow.hierarchical-child-binding:0.1:"
            + sha256(encoded).hexdigest(),
        )
