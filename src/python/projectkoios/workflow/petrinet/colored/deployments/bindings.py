"""Content-identified deployment linking for immutable execution plans."""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from string import hexdigits

from ..children.exports.evidence import WorkflowChildExportEvidenceBinding
from ..children.interfaces import WorkflowCompanionProductionPhase
from ..plans.definition import WorkflowExecutionPlan
from ..plans.identities import WorkflowExecutionPlanIdentity
from .linking import (
    WorkflowChildPlanExportCorrelationRequest,
    WorkflowChildPlanExportCorrelator,
    WorkflowChildPlanGraphValidationInput,
    WorkflowChildPlanGraphValidator,
    WorkflowChildPlanReference,
)


@dataclass(frozen=True, slots=True)
class WorkflowCompanionCapability:
    """Exact companion role, production phase, and supported bounds."""

    evidence_role_identity: str
    production_phase: WorkflowCompanionProductionPhase
    maximum_payload_bytes: int
    maximum_reference_count: int
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if (
            type(self.evidence_role_identity) is not str
            or not self.evidence_role_identity
        ):
            raise TypeError("evidence_role_identity must be a nonempty string")
        if not isinstance(
            self.production_phase, WorkflowCompanionProductionPhase
        ):
            raise TypeError(
                "production_phase must be WorkflowCompanionProductionPhase"
            )
        for name in ("maximum_payload_bytes", "maximum_reference_count"):
            value = getattr(self, name)
            if (
                type(value) is not int
                or not 1 <= value <= 9_223_372_036_854_775_807
            ):
                raise TypeError(
                    f"{name} must be a positive signed-64-bit integer"
                )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        encoded = json.dumps(
            {
                "contract_version": str(self.contract_version),
                "evidence_role_identity": self.evidence_role_identity,
                "maximum_payload_bytes": str(self.maximum_payload_bytes),
                "maximum_reference_count": str(self.maximum_reference_count),
                "production_phase": self.production_phase.value,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.companion-capability:0.1:"
            + sha256(encoded).hexdigest(),
        )


class WorkflowDeploymentCapabilityPhase(StrEnum):
    """Closed deployment phases implemented by one provider capability."""

    PROVISION = "provision"
    EXECUTE = "execute"
    ENVIRONMENT = "environment"
    RESOLVE_AND_RECONCILE = "resolve_and_reconcile"


@dataclass(frozen=True, slots=True)
class WorkflowProviderCapability:
    """Typed bounded provider behavior without executable callbacks."""

    capability_name: str
    phase: WorkflowDeploymentCapabilityPhase
    maximum_total_companion_reference_count: int
    companion_capabilities: tuple[WorkflowCompanionCapability, ...]
    protected_effect_capability_identities: tuple[str, ...]
    reconciliation_capability_identities: tuple[str, ...]
    protocol_requirement_identities: tuple[str, ...]
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.capability_name) is not str or not self.capability_name:
            raise TypeError("capability_name must be a nonempty string")
        if not isinstance(self.phase, WorkflowDeploymentCapabilityPhase):
            raise TypeError("phase must be WorkflowDeploymentCapabilityPhase")
        maximum_total = self.maximum_total_companion_reference_count
        if (
            type(maximum_total) is not int
            or not 0 <= maximum_total <= 9_223_372_036_854_775_807
        ):
            raise TypeError(
                "maximum_total_companion_reference_count must be a signed-64-bit nonnegative integer"
            )
        capabilities = self.companion_capabilities
        if type(capabilities) is not tuple or any(
            type(item) is not WorkflowCompanionCapability
            for item in capabilities
        ):
            raise TypeError(
                "companion_capabilities must contain exact WorkflowCompanionCapability records"
            )
        capability_identities = tuple(item.identity for item in capabilities)
        if capability_identities != tuple(sorted(set(capability_identities))):
            raise ValueError(
                "companion_capabilities must be unique and identity-ordered"
            )
        for name in (
            "protected_effect_capability_identities",
            "reconciliation_capability_identities",
            "protocol_requirement_identities",
        ):
            values = getattr(self, name)
            if type(values) is not tuple or any(
                type(item) is not str or not item for item in values
            ):
                raise TypeError(f"{name} must contain nonempty strings")
            if values != tuple(sorted(set(values))):
                raise ValueError(f"{name} must be unique and lexical")
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        encoded = json.dumps(
            {
                "capability_name": self.capability_name,
                "companion_capability_identities": list(capability_identities),
                "contract_version": str(self.contract_version),
                "maximum_total_companion_reference_count": str(maximum_total),
                "phase": self.phase.value,
                "protected_effect_capability_identities": list(
                    self.protected_effect_capability_identities
                ),
                "protocol_requirement_identities": list(
                    self.protocol_requirement_identities
                ),
                "reconciliation_capability_identities": list(
                    self.reconciliation_capability_identities
                ),
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.provider-capability:0.1:"
            + sha256(encoded).hexdigest(),
        )


class WorkflowDeploymentBindingKind(StrEnum):
    """Closed deployment descriptor roles."""

    PROVIDER = "provider"
    WORKER = "worker"
    ENVIRONMENT = "environment"
    RESOLVER = "resolver"


@dataclass(frozen=True, slots=True)
class WorkflowDeploymentBindingDescriptor:
    """One exact versioned deployment implementation/capability descriptor."""

    kind: WorkflowDeploymentBindingKind
    owner_identity: str
    implementation_identity: str
    version_identity: str
    capability: WorkflowProviderCapability
    protocol_identity: str
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, WorkflowDeploymentBindingKind):
            raise TypeError("kind must be WorkflowDeploymentBindingKind")
        for name in (
            "owner_identity",
            "implementation_identity",
            "version_identity",
            "protocol_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        if type(self.capability) is not WorkflowProviderCapability:
            raise TypeError("capability must be WorkflowProviderCapability")
        expected_phase = {
            WorkflowDeploymentBindingKind.PROVIDER: WorkflowDeploymentCapabilityPhase.PROVISION,
            WorkflowDeploymentBindingKind.WORKER: WorkflowDeploymentCapabilityPhase.EXECUTE,
            WorkflowDeploymentBindingKind.ENVIRONMENT: WorkflowDeploymentCapabilityPhase.ENVIRONMENT,
            WorkflowDeploymentBindingKind.RESOLVER: WorkflowDeploymentCapabilityPhase.RESOLVE_AND_RECONCILE,
        }[self.kind]
        if self.capability.phase is not expected_phase:
            raise ValueError(
                "capability phase must match deployment binding kind"
            )
        if (
            self.protocol_identity
            not in self.capability.protocol_requirement_identities
        ):
            raise ValueError(
                "capability protocol requirement must match descriptor protocol"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "capability_identity": self.capability.identity,
            "contract_version": str(self.contract_version),
            "implementation_identity": self.implementation_identity,
            "kind": self.kind.value,
            "owner_identity": self.owner_identity,
            "protocol_identity": self.protocol_identity,
            "version_identity": self.version_identity,
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
            "projectkoios.workflow.deployment-binding-descriptor:0.1:"
            + sha256(encoded).hexdigest(),
        )


@dataclass(frozen=True, slots=True)
class WorkflowExecutionBindingsIdentity:
    """Content-derived identity of one exact deployment linking."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("execution-bindings identity must be a string")
        prefix = "projectkoios.workflow.execution-bindings:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("execution-bindings identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError(
                "execution-bindings identity must end in lowercase SHA-256"
            )


@dataclass(frozen=True, slots=True)
class WorkflowExecutionBindings:
    """One exact deployment linking kept outside immutable plan semantics."""

    execution_plan: WorkflowExecutionPlan
    descriptors: tuple[WorkflowDeploymentBindingDescriptor, ...]
    child_plan_references: tuple[WorkflowChildPlanReference, ...]
    child_execution_plans: tuple[WorkflowExecutionPlan, ...]
    child_export_evidence_bindings: tuple[
        WorkflowChildExportEvidenceBinding, ...
    ]
    contract_version: int
    identity: WorkflowExecutionBindingsIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.execution_plan) is not WorkflowExecutionPlan:
            raise TypeError("execution_plan must be WorkflowExecutionPlan")
        descriptors = self.descriptors
        if type(descriptors) is not tuple or any(
            type(item) is not WorkflowDeploymentBindingDescriptor
            for item in descriptors
        ):
            raise TypeError(
                "descriptors must contain exact WorkflowDeploymentBindingDescriptor records"
            )
        descriptor_identities = tuple(item.identity for item in descriptors)
        if descriptor_identities != tuple(sorted(set(descriptor_identities))):
            raise ValueError("descriptors must be unique and identity-ordered")
        kinds = tuple(item.kind for item in descriptors)
        for required in (
            WorkflowDeploymentBindingKind.PROVIDER,
            WorkflowDeploymentBindingKind.WORKER,
            WorkflowDeploymentBindingKind.ENVIRONMENT,
            WorkflowDeploymentBindingKind.RESOLVER,
        ):
            if kinds.count(required) != 1:
                raise ValueError(
                    f"deployment linking requires exactly one {required.value} descriptor"
                )
        references = self.child_plan_references
        if type(references) is not tuple or any(
            type(item) is not WorkflowChildPlanReference for item in references
        ):
            raise TypeError(
                "child_plan_references must contain exact WorkflowChildPlanReference records"
            )
        reference_identities = tuple(item.identity for item in references)
        if reference_identities != tuple(sorted(set(reference_identities))):
            raise ValueError(
                "child_plan_references must be unique and identity-ordered"
            )
        direct_references = {
            (item.child_execution_plan_identity, item.child_export_identity)
            for item in references
            if item.parent_execution_plan_identity
            == self.execution_plan.identity
        }
        expected_direct_references = {
            (item.child_execution_plan_identity, item.child_export_identity)
            for item in self.execution_plan.closure.child_bindings
        }
        if direct_references != expected_direct_references:
            raise ValueError(
                "root child-plan references must exactly equal plan child bindings"
            )
        child_plans = self.child_execution_plans
        if type(child_plans) is not tuple or any(
            type(item) is not WorkflowExecutionPlan for item in child_plans
        ):
            raise TypeError(
                "child_execution_plans must contain exact WorkflowExecutionPlan records"
            )
        child_plan_identities = tuple(item.identity for item in child_plans)
        child_plan_identity_values = tuple(
            item.value for item in child_plan_identities
        )
        if child_plan_identity_values != tuple(
            sorted(set(child_plan_identity_values))
        ):
            raise ValueError(
                "child_execution_plans must be unique and identity-ordered"
            )
        retained_child_identities = set(child_plan_identities)
        referenced_child_identities = {
            item.child_execution_plan_identity for item in references
        }
        if retained_child_identities != referenced_child_identities:
            raise ValueError(
                "retained child plans must exactly resolve all child-plan references"
            )
        admitted_parent_identities = {
            self.execution_plan.identity,
            *retained_child_identities,
        }
        if any(
            item.parent_execution_plan_identity
            not in admitted_parent_identities
            for item in references
        ):
            raise ValueError(
                "every child-plan reference parent must be a retained plan"
            )
        plans_by_identity = {
            item.identity: item for item in (self.execution_plan, *child_plans)
        }
        for parent_identity, parent_plan in plans_by_identity.items():
            actual_children = {
                (item.child_execution_plan_identity, item.child_export_identity)
                for item in references
                if item.parent_execution_plan_identity == parent_identity
            }
            expected_children = {
                (item.child_execution_plan_identity, item.child_export_identity)
                for item in parent_plan.closure.child_bindings
            }
            if actual_children != expected_children:
                raise ValueError(
                    "each retained plan's child references must exactly equal its child bindings"
                )
        graph_result = WorkflowChildPlanGraphValidator().execute(
            WorkflowChildPlanGraphValidationInput(
                self.execution_plan.identity, references
            )
        )
        if not graph_result.is_valid:
            codes = ",".join(item.code.value for item in graph_result.issues)
            raise ValueError(f"invalid child-plan reference graph: {codes}")
        evidence = self.child_export_evidence_bindings
        if type(evidence) is not tuple or any(
            type(item) is not WorkflowChildExportEvidenceBinding
            for item in evidence
        ):
            raise TypeError(
                "child_export_evidence_bindings must contain exact evidence bindings"
            )
        evidence_identities = tuple(item.identity.value for item in evidence)
        if evidence_identities != tuple(sorted(set(evidence_identities))):
            raise ValueError(
                "child_export_evidence_bindings must be unique and identity-ordered"
            )
        expected_exports = {
            (item.child_execution_plan_identity, item.child_export_identity)
            for item in references
        }
        retained_exports = {
            (
                item.child_export.closure.execution_plan_identity,
                item.child_export.identity,
            )
            for item in evidence
        }
        if retained_exports != expected_exports:
            raise ValueError(
                "child-export evidence bindings must exactly resolve child-plan references"
            )
        evidence_by_export = {
            item.child_export.identity: item.child_export for item in evidence
        }
        child_plans_by_identity = {item.identity: item for item in child_plans}
        for evidence_binding in evidence:
            child_export = evidence_binding.child_export
            retained_child_plan = child_plans_by_identity[
                child_export.closure.execution_plan_identity
            ]
            correlation = WorkflowChildPlanExportCorrelator().execute(
                WorkflowChildPlanExportCorrelationRequest(
                    retained_child_plan, child_export
                )
            )
            if not correlation.is_correlated:
                raise ValueError(
                    "child export must equal the exact retained child plan closure: "
                    + ",".join(correlation.mismatched_field_names)
                )
        all_child_bindings = tuple(
            item
            for plan in (self.execution_plan, *child_plans)
            for item in plan.closure.child_bindings
        )
        for child_binding in all_child_bindings:
            child_export = evidence_by_export[
                child_binding.child_export_identity
            ]
            interface = child_export.closure.interface
            if (
                child_export.closure.execution_plan_identity
                != child_binding.child_execution_plan_identity
            ):
                raise ValueError(
                    "child export must identify the bound child execution plan"
                )
            if child_binding.input_mapping.child_input_port_identity not in {
                item.identity for item in interface.input_ports
            }:
                raise ValueError(
                    "child input mapping must name an exported input port"
                )
            mapped_requirements = tuple(
                item.terminal_delivery_requirement
                for item in child_binding.terminal_mappings
            )
            if mapped_requirements != interface.terminal_delivery_requirements:
                raise ValueError(
                    "child terminal mappings must exactly equal exported requirements"
                )
            if (
                child_binding.cancellation_propagation_policy_identity
                != interface.cancellation_capability.propagation_policy_identity
            ):
                raise ValueError(
                    "child cancellation policy must equal the exported policy"
                )
        descriptor_by_kind = {item.kind: item for item in descriptors}
        interfaces = tuple(
            plan.closure.child_interface
            for plan in (self.execution_plan, *child_plans)
            if plan.closure.child_interface is not None
        )
        delivery_requirements = tuple(
            requirement
            for interface in interfaces
            for requirement in interface.terminal_delivery_requirements
        )
        companion_requirements = tuple(
            companion
            for requirement in delivery_requirements
            for companion in requirement.companion_requirements
        )
        maximum_required_companions = max(
            (
                requirement.maximum_total_companion_reference_count
                for requirement in delivery_requirements
            ),
            default=0,
        )
        protected_effects_required = {
            identity
            for plan in (self.execution_plan, *child_plans)
            for route in plan.closure.transition_routes
            if route.protected_effect_capability_identity is not None
            for identity in (route.protected_effect_capability_identity,)
        } | {
            identity
            for interface in interfaces
            for identity in interface.protected_effect_capability_identities
        }
        reconciliation_required = {
            interface.reconciliation_capability_identity
            for interface in interfaces
        }
        protocols_required = {
            interface.execution_protocol_requirement_identity
            for interface in interfaces
        }
        resolver_capability = descriptor_by_kind[
            WorkflowDeploymentBindingKind.RESOLVER
        ].capability
        worker_capability = descriptor_by_kind[
            WorkflowDeploymentBindingKind.WORKER
        ].capability
        if (
            maximum_required_companions
            > resolver_capability.maximum_total_companion_reference_count
        ):
            raise ValueError(
                "resolver capability does not satisfy companion delivery bounds"
            )
        supported_companions = resolver_capability.companion_capabilities
        for requirement in companion_requirements:
            if not any(
                capability.evidence_role_identity
                == requirement.evidence_role_identity
                and capability.production_phase is requirement.production_phase
                and capability.maximum_payload_bytes
                >= requirement.maximum_payload_bytes
                and capability.maximum_reference_count
                >= requirement.maximum_reference_count
                for capability in supported_companions
            ):
                raise ValueError(
                    "resolver capability does not satisfy a companion role, phase, or bound"
                )
        if not reconciliation_required <= set(
            resolver_capability.reconciliation_capability_identities
        ):
            raise ValueError(
                "resolver capability does not satisfy child reconciliation identities"
            )
        if not protocols_required <= set(
            resolver_capability.protocol_requirement_identities
        ):
            raise ValueError(
                "resolver capability does not satisfy child protocol requirements"
            )
        if not protected_effects_required <= set(
            worker_capability.protected_effect_capability_identities
        ):
            raise ValueError(
                "worker capability does not admit required protected effects"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "child_execution_plan_identities": [
                item.value for item in child_plan_identities
            ],
            "child_export_evidence_binding_identities": list(
                evidence_identities
            ),
            "child_plan_reference_identities": list(reference_identities),
            "contract_version": str(self.contract_version),
            "descriptor_identities": list(descriptor_identities),
            "execution_plan_identity": self.execution_plan.identity.value,
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
            WorkflowExecutionBindingsIdentity(
                "projectkoios.workflow.execution-bindings:0.1:"
                + sha256(encoded).hexdigest()
            ),
        )

    @property
    def execution_plan_identity(self) -> WorkflowExecutionPlanIdentity:
        """Return the exact retained execution-plan identity."""
        return self.execution_plan.identity
