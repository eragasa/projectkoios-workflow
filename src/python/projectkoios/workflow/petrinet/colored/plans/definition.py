"""Immutable execution-plan closure, construction, and identity."""

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final

from ..canonical.definitions import (
    CpnCanonicalDefinition,
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionDecodingInput,
    CpnCanonicalDefinitionIdentity,
)
from ..children.bindings import WorkflowHierarchicalChildBinding
from ..children.interfaces import (
    WorkflowChildInterface,
    WorkflowTerminalDeliveryRequirement,
)
from ..definitions import CpnDefinitionIdentity
from ..mappings.values import WorkflowValueMappingDescriptor
from ..payloads.bindings import WorkflowPayloadColorBinding
from ..profiles.definition import WorkflowCpnExecutionProfileIdentity
from ..routes.transitions import (
    WorkflowTransitionRoute,
    WorkflowTransitionRouteKind,
)
from .identities import WorkflowExecutionPlanIdentity


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanClosure:
    """Small owner-only closed semantic inputs to plan identity derivation."""

    nominal_definition_identity: CpnDefinitionIdentity
    canonical_definition: CpnCanonicalDefinition
    cpn_execution_profile_identity: WorkflowCpnExecutionProfileIdentity
    initial_marking_contract_identity: str
    payload_color_bindings: tuple[WorkflowPayloadColorBinding, ...]
    transition_routes: tuple[WorkflowTransitionRoute, ...]
    child_bindings: tuple[WorkflowHierarchicalChildBinding, ...]
    child_interface: WorkflowChildInterface | None
    terminal_delivery_requirements: tuple[
        WorkflowTerminalDeliveryRequirement, ...
    ]
    owner_mapping_descriptors: tuple[WorkflowValueMappingDescriptor, ...]
    compiler_identity: str
    compiler_version: str
    contract_version: int

    def __post_init__(self) -> None:
        if type(self.nominal_definition_identity) is not CpnDefinitionIdentity:
            raise TypeError(
                "nominal_definition_identity must be CpnDefinitionIdentity"
            )
        if type(self.canonical_definition) is not CpnCanonicalDefinition:
            raise TypeError(
                "canonical_definition must be CpnCanonicalDefinition"
            )
        decoded_definition = (
            CpnCanonicalDefinitionCodec()
            .decode(
                CpnCanonicalDefinitionDecodingInput(self.canonical_definition)
            )
            .definition
        )
        if decoded_definition.identity != self.nominal_definition_identity:
            raise ValueError(
                "canonical definition must encode the nominal plan definition"
            )
        for name in (
            "initial_marking_contract_identity",
            "compiler_identity",
            "compiler_version",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if type(self.cpn_execution_profile_identity) is not (
            WorkflowCpnExecutionProfileIdentity
        ):
            raise TypeError(
                "cpn_execution_profile_identity must be "
                "WorkflowCpnExecutionProfileIdentity"
            )
        if type(self.payload_color_bindings) is not tuple or any(
            type(item) is not WorkflowPayloadColorBinding
            for item in self.payload_color_bindings
        ):
            raise TypeError(
                "payload_color_bindings must contain exact WorkflowPayloadColorBinding records"
            )
        payload_binding_identities = tuple(
            item.identity for item in self.payload_color_bindings
        )
        if payload_binding_identities != tuple(
            sorted(set(payload_binding_identities))
        ):
            raise ValueError(
                "payload_color_bindings must be unique and identity-ordered"
            )
        if any(
            item.definition_identity != self.nominal_definition_identity
            for item in self.payload_color_bindings
        ):
            raise ValueError(
                "payload color bindings must name the plan definition"
            )
        admitted_colors = {item.identity for item in decoded_definition.colors}
        if any(
            item.color_identity not in admitted_colors
            for item in self.payload_color_bindings
        ):
            raise ValueError(
                "payload color bindings must name canonical-definition colors"
            )
        if (
            self.child_interface is not None
            and type(self.child_interface) is not WorkflowChildInterface
        ):
            raise TypeError(
                "child_interface must be WorkflowChildInterface or None"
            )
        if type(self.transition_routes) is not tuple or any(
            type(item) is not WorkflowTransitionRoute
            for item in self.transition_routes
        ):
            raise TypeError(
                "transition_routes must contain exact WorkflowTransitionRoute records"
            )
        route_identities = tuple(
            item.identity for item in self.transition_routes
        )
        if route_identities != tuple(sorted(set(route_identities))):
            raise ValueError(
                "transition_routes must be unique and identity-ordered"
            )
        if any(
            item.definition_identity != self.nominal_definition_identity
            for item in self.transition_routes
        ):
            raise ValueError("transition routes must name the plan definition")
        admitted_transitions = {
            item.identity for item in decoded_definition.transitions
        }
        if any(
            item.transition_identity not in admitted_transitions
            for item in self.transition_routes
        ):
            raise ValueError(
                "transition routes must name canonical-definition transitions"
            )
        if type(self.child_bindings) is not tuple or any(
            type(item) is not WorkflowHierarchicalChildBinding
            for item in self.child_bindings
        ):
            raise TypeError(
                "child_bindings must contain exact WorkflowHierarchicalChildBinding records"
            )
        child_binding_identities = tuple(
            item.identity for item in self.child_bindings
        )
        if child_binding_identities != tuple(
            sorted(set(child_binding_identities))
        ):
            raise ValueError(
                "child_bindings must be unique and identity-ordered"
            )
        if any(
            item.parent_definition_identity != self.nominal_definition_identity
            for item in self.child_bindings
        ):
            raise ValueError("child bindings must name the plan definition")
        admitted_places = {item.identity for item in decoded_definition.places}
        if any(
            item.input_mapping.parent_place_identity not in admitted_places
            or item.input_mapping.parent_color_identity not in admitted_colors
            for item in self.child_bindings
        ):
            raise ValueError(
                "child input mappings must name canonical-definition places and colors"
            )
        hierarchical_route_identities = tuple(
            item.identity
            for item in self.transition_routes
            if item.kind is WorkflowTransitionRouteKind.HIERARCHICAL_CHILD
        )
        bound_route_identities = tuple(
            item.transition_route.identity for item in self.child_bindings
        )
        if tuple(sorted(bound_route_identities)) != tuple(
            sorted(hierarchical_route_identities)
        ):
            raise ValueError(
                "every hierarchical route must have exactly one child binding"
            )
        requirements = self.terminal_delivery_requirements
        if type(requirements) is not tuple or any(
            type(item) is not WorkflowTerminalDeliveryRequirement
            for item in requirements
        ):
            raise TypeError(
                "terminal_delivery_requirements must contain exact requirements"
            )
        requirement_identities = tuple(item.identity for item in requirements)
        if requirement_identities != tuple(sorted(set(requirement_identities))):
            raise ValueError(
                "terminal_delivery_requirements must be unique and identity-ordered"
            )
        if self.child_interface is not None and (
            requirements != self.child_interface.terminal_delivery_requirements
        ):
            raise ValueError(
                "plan terminal requirements must equal its child interface"
            )
        descriptors = self.owner_mapping_descriptors
        if type(descriptors) is not tuple or any(
            type(item) is not WorkflowValueMappingDescriptor
            for item in descriptors
        ):
            raise TypeError(
                "owner_mapping_descriptors must contain exact descriptors"
            )
        descriptor_identities = tuple(item.identity for item in descriptors)
        if descriptor_identities != tuple(sorted(set(descriptor_identities))):
            raise ValueError(
                "owner_mapping_descriptors must be unique and identity-ordered"
            )
        referenced_descriptor_identities = {
            descriptor.identity
            for route in self.transition_routes
            for descriptor in route.mapping_descriptors
        }
        referenced_descriptor_identities.update(
            binding.input_mapping.mapping_descriptor.identity
            for binding in self.child_bindings
        )
        referenced_descriptor_identities.update(
            mapping.parent_external_output_mapping_descriptor.identity
            for binding in self.child_bindings
            for mapping in binding.terminal_mappings
        )
        if set(descriptor_identities) != referenced_descriptor_identities:
            raise ValueError(
                "owner_mapping_descriptors must exactly equal route and child mappings"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")

    @property
    def canonical_definition_identity(self) -> CpnCanonicalDefinitionIdentity:
        """Return the content identity derived with the retained bytes."""
        return self.canonical_definition.identity

    @property
    def canonical_definition_representation_profile_identity(self) -> str:
        """Return the retained canonical-definition representation profile."""
        return self.canonical_definition.representation_profile_identity

    @property
    def canonical_definition_sha256(self) -> str:
        """Return the digest of the exact retained canonical-definition bytes."""
        return self.canonical_definition.sha256


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanIdentityDeriverIdentity:
    """Identity of exact execution-plan identity derivation semantics."""

    value: str = "projectkoios.workflow.cpn.execution-plan-identity-deriver:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanIdentityDerivationInput:
    """One complete execution-plan closure to identify."""

    closure: WorkflowExecutionPlanClosure

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowExecutionPlanClosure:
            raise TypeError("closure must be WorkflowExecutionPlanClosure")


@final
class WorkflowExecutionPlanIdentityDeriver:
    """Directly derive plan identity from complete immutable semantic closure."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowExecutionPlanIdentityDeriverIdentity:
        """Return exact derivation semantics identity."""
        return WorkflowExecutionPlanIdentityDeriverIdentity()

    def execute(
        self, derivation_input: WorkflowExecutionPlanIdentityDerivationInput
    ) -> WorkflowExecutionPlanIdentity:
        """Hash every semantic plan-closure field exactly once."""
        if (
            type(derivation_input)
            is not WorkflowExecutionPlanIdentityDerivationInput
        ):
            raise TypeError(
                "derivation_input must be "
                "WorkflowExecutionPlanIdentityDerivationInput"
            )
        closure = derivation_input.closure
        state = {
            "canonical_definition_identity": closure.canonical_definition_identity.value,
            "canonical_definition_representation_profile_identity": (
                closure.canonical_definition_representation_profile_identity
            ),
            "canonical_definition_sha256": closure.canonical_definition_sha256,
            "child_binding_identities": [
                item.identity for item in closure.child_bindings
            ],
            "child_interface_identity": (
                None
                if closure.child_interface is None
                else closure.child_interface.identity
            ),
            "compiler_identity": closure.compiler_identity,
            "compiler_version": closure.compiler_version,
            "contract_version": str(closure.contract_version),
            "cpn_execution_profile_identity": (
                closure.cpn_execution_profile_identity.value
            ),
            "initial_marking_contract_identity": (
                closure.initial_marking_contract_identity
            ),
            "nominal_definition_identity": closure.nominal_definition_identity.value,
            "owner_mapping_descriptor_identities": [
                item.identity for item in closure.owner_mapping_descriptors
            ],
            "payload_color_binding_identities": [
                item.identity for item in closure.payload_color_bindings
            ],
            "transition_route_identities": [
                item.identity for item in closure.transition_routes
            ],
            "terminal_delivery_requirement_identities": [
                item.identity for item in closure.terminal_delivery_requirements
            ],
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return WorkflowExecutionPlanIdentity(
            "projectkoios.workflow.execution-plan:0.1:"
            + sha256(encoded).hexdigest()
        )


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlan:
    """One complete immutable plan closure and content identity."""

    closure: WorkflowExecutionPlanClosure
    identity: WorkflowExecutionPlanIdentity
    canonical_sha256: str

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowExecutionPlanClosure:
            raise TypeError("closure must be WorkflowExecutionPlanClosure")
        if type(self.identity) is not WorkflowExecutionPlanIdentity:
            raise TypeError("identity must be WorkflowExecutionPlanIdentity")
        if self.canonical_sha256 != self.identity.value.rsplit(":", 1)[-1]:
            raise ValueError(
                "canonical_sha256 must equal the execution-plan identity digest"
            )
        derived = WorkflowExecutionPlanIdentityDeriver().execute(
            WorkflowExecutionPlanIdentityDerivationInput(self.closure)
        )
        if derived != self.identity:
            raise ValueError(
                "execution-plan identity does not match its closure"
            )


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanCompilerIdentity:
    """Identity of exact immutable execution-plan assembly semantics."""

    value: str = "projectkoios.workflow.cpn.execution-plan-compiler:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowExecutionPlanCompilationInput:
    """Complete semantic closure to compile as one execution plan."""

    closure: WorkflowExecutionPlanClosure

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowExecutionPlanClosure:
            raise TypeError("closure must be WorkflowExecutionPlanClosure")


@final
class WorkflowExecutionPlanCompiler:
    """Directly assemble an immutable identity-closed execution plan."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowExecutionPlanCompilerIdentity:
        """Return exact plan assembly semantics identity."""
        return WorkflowExecutionPlanCompilerIdentity()

    def execute(
        self, compilation_input: WorkflowExecutionPlanCompilationInput
    ) -> WorkflowExecutionPlan:
        """Derive and retain the exact plan identity and canonical digest."""
        if type(compilation_input) is not WorkflowExecutionPlanCompilationInput:
            raise TypeError(
                "compilation_input must be WorkflowExecutionPlanCompilationInput"
            )
        identity = WorkflowExecutionPlanIdentityDeriver().execute(
            WorkflowExecutionPlanIdentityDerivationInput(
                compilation_input.closure
            )
        )
        return WorkflowExecutionPlan(
            compilation_input.closure,
            identity,
            identity.value.rsplit(":", 1)[-1],
        )
