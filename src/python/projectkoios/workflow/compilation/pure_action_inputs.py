"""Experimental plan closure for pure-action input-source mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from string import hexdigits

from projectkoios.workflow.actions import (
    ExperimentalWorkflowPureActionInputMappingDescriptor,
)
from projectkoios.workflow.core.identities import stable_identity

from .pure_action import (
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionExecutionPlan,
)

_INPUT_PLAN_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-input-plan:1"
)
_INPUT_BINDINGS_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-input-bindings:1"
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputPlanIdentity:
    """Content identity of one input-extended pure-action plan candidate."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action input plan identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputBindingsIdentity:
    """Content identity of one input-extended deployment candidate."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "pure action input bindings identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputPlan:
    """Extend one replayable plan with ordered input-source semantics."""

    identity: ExperimentalWorkflowPureActionInputPlanIdentity = field(
        init=False
    )
    execution_plan: ExperimentalWorkflowPureActionExecutionPlan
    input_mappings: tuple[
        ExperimentalWorkflowPureActionInputMappingDescriptor, ...
    ]

    def __post_init__(self) -> None:
        if type(self.execution_plan) is not (
            ExperimentalWorkflowPureActionExecutionPlan
        ):
            raise TypeError(
                "execution_plan must be "
                "ExperimentalWorkflowPureActionExecutionPlan"
            )
        plan = ExperimentalWorkflowPureActionExecutionPlan(
            selected_binding_profile_identity=(
                self.execution_plan.selected_binding_profile_identity
            ),
            output_mapping_descriptor=(
                self.execution_plan.output_mapping_descriptor
            ),
        )
        if plan != self.execution_plan:
            raise ValueError("execution plan differs after validation")
        if type(self.input_mappings) is not tuple:
            raise TypeError("input_mappings must be a tuple")
        reconstructed = tuple(
            _reconstruct_mapping(value) for value in self.input_mappings
        )
        if reconstructed != self.input_mappings:
            raise ValueError("input mappings differ after validation")
        transition_binding = plan.output_mapping_descriptor.transition_binding
        descriptor = plan.output_mapping_descriptor.firer_descriptor
        mapping_roles = tuple(value.input_role for value in reconstructed)
        contract_roles = tuple(
            value.role for value in descriptor.input_contracts
        )
        if mapping_roles != transition_binding.input_roles:
            raise ValueError(
                "input mappings must exactly follow transition input roles"
            )
        if mapping_roles != contract_roles:
            raise ValueError(
                "input mappings must exactly follow firer input contracts"
            )
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInputPlanIdentity(
                stable_identity(
                    _INPUT_PLAN_DOMAIN,
                    plan.identity.value,
                    tuple(value.identity.value for value in reconstructed),
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputBindings:
    """Link one input-extended plan to exact deployment bindings."""

    identity: ExperimentalWorkflowPureActionInputBindingsIdentity = field(
        init=False
    )
    input_plan: ExperimentalWorkflowPureActionInputPlan
    execution_bindings: ExperimentalWorkflowPureActionExecutionBindings

    def __post_init__(self) -> None:
        if type(self.input_plan) is not ExperimentalWorkflowPureActionInputPlan:
            raise TypeError(
                "input_plan must be ExperimentalWorkflowPureActionInputPlan"
            )
        input_plan = ExperimentalWorkflowPureActionInputPlan(
            execution_plan=self.input_plan.execution_plan,
            input_mappings=self.input_plan.input_mappings,
        )
        if input_plan != self.input_plan:
            raise ValueError("input plan differs after validation")
        if type(self.execution_bindings) is not (
            ExperimentalWorkflowPureActionExecutionBindings
        ):
            raise TypeError(
                "execution_bindings must be "
                "ExperimentalWorkflowPureActionExecutionBindings"
            )
        bindings = ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=self.execution_bindings.execution_plan,
            integration_manifest=self.execution_bindings.integration_manifest,
        )
        if bindings != self.execution_bindings:
            raise ValueError("execution bindings differ after validation")
        if input_plan.execution_plan != bindings.execution_plan:
            raise ValueError(
                "input plan execution plan differs from deployment bindings"
            )
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInputBindingsIdentity(
                stable_identity(
                    _INPUT_BINDINGS_DOMAIN,
                    input_plan.identity.value,
                    bindings.identity.value,
                )
            ),
        )


def _reconstruct_mapping(
    value: ExperimentalWorkflowPureActionInputMappingDescriptor,
) -> ExperimentalWorkflowPureActionInputMappingDescriptor:
    if type(value) is not ExperimentalWorkflowPureActionInputMappingDescriptor:
        raise TypeError(
            "input mappings must contain "
            "ExperimentalWorkflowPureActionInputMappingDescriptor"
        )
    reconstructed = ExperimentalWorkflowPureActionInputMappingDescriptor(
        input_role=value.input_role,
        source_kind=value.source_kind,
        source_profile_identity=value.source_profile_identity,
        mapping_version=value.mapping_version,
    )
    if reconstructed != value:
        raise ValueError("input mapping differs after validation")
    return reconstructed


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


__all__ = [
    "ExperimentalWorkflowPureActionInputBindings",
    "ExperimentalWorkflowPureActionInputBindingsIdentity",
    "ExperimentalWorkflowPureActionInputPlan",
    "ExperimentalWorkflowPureActionInputPlanIdentity",
]
