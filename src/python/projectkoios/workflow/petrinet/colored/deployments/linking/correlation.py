"""Finite acyclic child-plan reference validation for deployment linking."""

from dataclasses import dataclass
from typing import final

from ...children.exports.definition import (
    WorkflowChildDefinitionExport,
)
from ...plans.compilation import WorkflowExecutionPlan

_MAXIMUM_CHILD_PLAN_REFERENCES = 4096


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanExportCorrelationRequest:
    """Complete retained child plan and exact export to correlate."""

    child_execution_plan: WorkflowExecutionPlan
    child_export: WorkflowChildDefinitionExport

    def __post_init__(self) -> None:
        if type(self.child_execution_plan) is not WorkflowExecutionPlan:
            raise TypeError(
                "child_execution_plan must be WorkflowExecutionPlan"
            )
        if type(self.child_export) is not WorkflowChildDefinitionExport:
            raise TypeError(
                "child_export must be WorkflowChildDefinitionExport"
            )


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanExportCorrelationResult:
    """Named exact mismatches between a retained plan and export closure."""

    mismatched_field_names: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.mismatched_field_names) is not tuple or any(
            type(item) is not str or not item
            for item in self.mismatched_field_names
        ):
            raise TypeError(
                "mismatched_field_names must contain nonempty strings"
            )
        if self.mismatched_field_names != tuple(
            sorted(set(self.mismatched_field_names))
        ):
            raise ValueError(
                "mismatched_field_names must be unique and lexical"
            )

    @property
    def is_correlated(self) -> bool:
        """Report whether every redundant export field matches the plan."""
        return not self.mismatched_field_names


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanExportCorrelatorIdentity:
    """Identity of exact child-plan/export closure correlation semantics."""

    value: str = "projectkoios.workflow.child-plan-export-correlator:0.1"


@final
class WorkflowChildPlanExportCorrelator:
    """Compare every redundant export field with its retained child plan."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowChildPlanExportCorrelatorIdentity:
        """Return exact child-plan/export correlation semantics identity."""
        return WorkflowChildPlanExportCorrelatorIdentity()

    def execute(
        self, request: WorkflowChildPlanExportCorrelationRequest
    ) -> WorkflowChildPlanExportCorrelationResult:
        """Return the exact lexical field names whose values disagree."""
        if type(request) is not WorkflowChildPlanExportCorrelationRequest:
            raise TypeError(
                "request must be WorkflowChildPlanExportCorrelationRequest"
            )
        export = request.child_export.closure
        plan = request.child_execution_plan
        closure = plan.closure
        compared = {
            "execution_plan_identity": export.execution_plan_identity
            == plan.identity,
            "execution_plan_sha256": export.execution_plan_sha256
            == plan.identity.value.rsplit(":", 1)[-1],
            "nominal_definition_identity": export.nominal_definition_identity
            == closure.nominal_definition_identity.value,
            "canonical_definition_identity": export.canonical_definition_identity
            == closure.canonical_definition.identity.value,
            "canonical_definition_representation_profile_identity": export.canonical_definition_representation_profile_identity
            == closure.canonical_definition.representation_profile_identity,
            "canonical_definition_sha256": export.canonical_definition_sha256
            == closure.canonical_definition.sha256,
            "cpn_execution_profile_identity": export.cpn_execution_profile_identity
            == closure.cpn_execution_profile_identity,
            "initial_marking_constructor_identity": export.initial_marking_constructor_identity
            == closure.initial_marking_contract_identity,
            "interface": export.interface == closure.child_interface,
            "compiler_implementation_identity": export.compiler_implementation_identity
            == closure.compiler_identity,
            "compiler_version_identity": export.compiler_version_identity
            == closure.compiler_version,
        }
        return WorkflowChildPlanExportCorrelationResult(
            tuple(
                sorted(
                    name for name, matches in compared.items() if not matches
                )
            )
        )
