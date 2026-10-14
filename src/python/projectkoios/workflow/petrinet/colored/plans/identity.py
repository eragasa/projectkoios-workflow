"""Immutable execution-plan closure, construction, and identity."""

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final

from .definition import WorkflowExecutionPlanClosure
from .identities import WorkflowExecutionPlanIdentity


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
