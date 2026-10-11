"""Finite acyclic child-plan reference validation for deployment linking."""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import final

from ..children.exports.definition import (
    WorkflowChildDefinitionExport,
    WorkflowChildDefinitionExportIdentity,
)
from ..plans.definition import WorkflowExecutionPlan
from ..plans.identities import WorkflowExecutionPlanIdentity

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


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanReference:
    """One parent-plan reference to one separately identified child export/plan."""

    parent_execution_plan_identity: WorkflowExecutionPlanIdentity
    child_execution_plan_identity: WorkflowExecutionPlanIdentity
    child_export_identity: WorkflowChildDefinitionExportIdentity
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if (
            type(self.parent_execution_plan_identity)
            is not WorkflowExecutionPlanIdentity
        ):
            raise TypeError(
                "parent_execution_plan_identity must be WorkflowExecutionPlanIdentity"
            )
        if (
            type(self.child_execution_plan_identity)
            is not WorkflowExecutionPlanIdentity
        ):
            raise TypeError(
                "child_execution_plan_identity must be WorkflowExecutionPlanIdentity"
            )
        if (
            type(self.child_export_identity)
            is not WorkflowChildDefinitionExportIdentity
        ):
            raise TypeError(
                "child_export_identity must be WorkflowChildDefinitionExportIdentity"
            )
        if type(self.contract_version) is not int or self.contract_version < 1:
            raise TypeError("contract_version must be a positive integer")
        state = {
            "child_execution_plan_identity": self.child_execution_plan_identity.value,
            "child_export_identity": self.child_export_identity.value,
            "contract_version": str(self.contract_version),
            "parent_execution_plan_identity": self.parent_execution_plan_identity.value,
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
            "projectkoios.workflow.child-plan-reference:0.1:"
            + sha256(encoded).hexdigest(),
        )


class WorkflowChildPlanGraphValidationIssueCode(StrEnum):
    """Closed child-plan reference graph failures."""

    SELF_REFERENCE = "self_reference"
    CYCLE = "cycle"
    UNREACHABLE_REFERENCE = "unreachable_reference"


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanGraphValidationIssue:
    """One deterministic child-plan graph finding."""

    code: WorkflowChildPlanGraphValidationIssueCode
    plan_identity_values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanGraphValidationInput:
    """One root plan and its complete bounded transitive reference set."""

    root_execution_plan_identity: WorkflowExecutionPlanIdentity
    references: tuple[WorkflowChildPlanReference, ...]

    def __post_init__(self) -> None:
        if (
            type(self.root_execution_plan_identity)
            is not WorkflowExecutionPlanIdentity
        ):
            raise TypeError(
                "root_execution_plan_identity must be WorkflowExecutionPlanIdentity"
            )
        if type(self.references) is not tuple or any(
            type(item) is not WorkflowChildPlanReference
            for item in self.references
        ):
            raise TypeError(
                "references must contain exact WorkflowChildPlanReference records"
            )
        if len(self.references) > _MAXIMUM_CHILD_PLAN_REFERENCES:
            raise ValueError("child-plan reference bound exceeded")
        identities = tuple(item.identity for item in self.references)
        if identities != tuple(sorted(set(identities))):
            raise ValueError("references must be unique and identity-ordered")


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanGraphValidationResult:
    """Complete deterministic child-plan reference graph findings."""

    issues: tuple[WorkflowChildPlanGraphValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether the supplied transitive child-plan graph is valid."""
        return not self.issues


@dataclass(frozen=True, slots=True)
class WorkflowChildPlanGraphValidatorIdentity:
    """Identity of finite acyclic child-plan reference validation semantics."""

    value: str = "projectkoios.workflow.child-plan-graph-validator:0.1"


@final
class WorkflowChildPlanGraphValidator:
    """Validate only static plan references, never CPN transition topology."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowChildPlanGraphValidatorIdentity:
        """Return exact child-plan graph validation semantics identity."""
        return WorkflowChildPlanGraphValidatorIdentity()

    def execute(
        self, validation_input: WorkflowChildPlanGraphValidationInput
    ) -> WorkflowChildPlanGraphValidationResult:
        """Reject self-reference, unreachable evidence, and static cycles."""
        if type(validation_input) is not WorkflowChildPlanGraphValidationInput:
            raise TypeError(
                "validation_input must be WorkflowChildPlanGraphValidationInput"
            )
        issues: list[WorkflowChildPlanGraphValidationIssue] = []
        adjacency: dict[str, set[str]] = {}
        all_nodes = {validation_input.root_execution_plan_identity.value}
        for reference in validation_input.references:
            parent = reference.parent_execution_plan_identity.value
            child = reference.child_execution_plan_identity.value
            all_nodes.update((parent, child))
            adjacency.setdefault(parent, set()).add(child)
            adjacency.setdefault(child, set())
            if parent == child:
                issues.append(
                    WorkflowChildPlanGraphValidationIssue(
                        WorkflowChildPlanGraphValidationIssueCode.SELF_REFERENCE,
                        (parent,),
                    )
                )
        reachable = {validation_input.root_execution_plan_identity.value}
        frontier = list(reachable)
        while frontier:
            parent = frontier.pop()
            for child in sorted(adjacency.get(parent, ())):
                if child not in reachable:
                    reachable.add(child)
                    frontier.append(child)
        unreachable = tuple(sorted(all_nodes - reachable))
        if unreachable:
            issues.append(
                WorkflowChildPlanGraphValidationIssue(
                    WorkflowChildPlanGraphValidationIssueCode.UNREACHABLE_REFERENCE,
                    unreachable,
                )
            )
        reachable_adjacency = {
            node: {
                child for child in adjacency.get(node, ()) if child in reachable
            }
            for node in reachable
        }
        indegree = {node: 0 for node in reachable}
        for children in reachable_adjacency.values():
            for child in children:
                indegree[child] += 1
        ready = sorted(node for node, degree in indegree.items() if degree == 0)
        visited: list[str] = []
        while ready:
            node = ready.pop(0)
            visited.append(node)
            for child in sorted(reachable_adjacency[node]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
                    ready.sort()
        cyclic = tuple(
            sorted(node for node, degree in indegree.items() if degree > 0)
        )
        if cyclic:
            issues.append(
                WorkflowChildPlanGraphValidationIssue(
                    WorkflowChildPlanGraphValidationIssueCode.CYCLE,
                    cyclic,
                )
            )
        return WorkflowChildPlanGraphValidationResult(tuple(issues))
