"""Cross-object validation for CPN profiles, plans, and child exports."""

from dataclasses import dataclass
from enum import StrEnum
from typing import final

from ..children.exports.definition import WorkflowChildDefinitionExportClosure
from ..plans.definition import WorkflowExecutionPlanClosure
from ..plans.identity import (
    WorkflowExecutionPlanIdentityDerivationInput,
    WorkflowExecutionPlanIdentityDeriver,
)
from ..plans.identities import WorkflowExecutionPlanIdentity
from ..profiles.definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileIdentity,
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
)


class WorkflowCpnClosureCorrelationIssueCode(StrEnum):
    """Closed profile/plan/export correlation failures."""

    PLAN_PROFILE_MISMATCH = "plan_profile_mismatch"
    EXPORT_PROFILE_MISMATCH = "export_profile_mismatch"
    EXPORT_PLAN_MISMATCH = "export_plan_mismatch"
    EXPORT_DEFINITION_MISMATCH = "export_definition_mismatch"
    EXPORT_INTERFACE_MISMATCH = "export_interface_mismatch"


@dataclass(frozen=True, slots=True)
class WorkflowCpnClosureCorrelationIssue:
    """One exact cross-closure mismatch."""

    code: WorkflowCpnClosureCorrelationIssueCode
    path: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkflowCpnClosureCorrelationInput:
    """Profile, plan, and export closures with their claimed identities."""

    profile: WorkflowCpnExecutionProfile
    profile_identity: WorkflowCpnExecutionProfileIdentity
    plan: WorkflowExecutionPlanClosure
    plan_identity: WorkflowExecutionPlanIdentity
    export: WorkflowChildDefinitionExportClosure


@dataclass(frozen=True, slots=True)
class WorkflowCpnClosureCorrelationResult:
    """Complete deterministic profile/plan/export mismatches."""

    issues: tuple[WorkflowCpnClosureCorrelationIssue, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether all redundant closure identities agree exactly."""
        return not self.issues


@dataclass(frozen=True, slots=True)
class WorkflowCpnClosureCorrelationValidatorIdentity:
    """Identity of exact profile/plan/export correlation semantics."""

    value: str = "projectkoios.workflow.cpn.closure-correlation-validator:0.1"


@final
class WorkflowCpnClosureCorrelationValidator:
    """Directly close every redundant profile, plan, and export correlation."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowCpnClosureCorrelationValidatorIdentity:
        """Return exact correlation semantics identity."""
        return WorkflowCpnClosureCorrelationValidatorIdentity()

    def execute(
        self, correlation_input: WorkflowCpnClosureCorrelationInput
    ) -> WorkflowCpnClosureCorrelationResult:
        """Re-derive identities and reject every stale subordinate correlation."""
        if type(correlation_input) is not WorkflowCpnClosureCorrelationInput:
            raise TypeError(
                "correlation_input must be WorkflowCpnClosureCorrelationInput"
            )
        issues: list[WorkflowCpnClosureCorrelationIssue] = []
        actual_profile = WorkflowCpnExecutionProfileIdentityDeriver().execute(
            WorkflowCpnExecutionProfileIdentityDerivationInput(
                correlation_input.profile
            )
        )
        if actual_profile != correlation_input.profile_identity or (
            correlation_input.plan.cpn_execution_profile_identity
            != correlation_input.profile_identity
        ):
            issues.append(
                WorkflowCpnClosureCorrelationIssue(
                    WorkflowCpnClosureCorrelationIssueCode.PLAN_PROFILE_MISMATCH,
                    ("plan", "cpn_execution_profile_identity"),
                )
            )
        actual_plan = WorkflowExecutionPlanIdentityDeriver().execute(
            WorkflowExecutionPlanIdentityDerivationInput(correlation_input.plan)
        )
        if actual_plan != correlation_input.plan_identity:
            issues.append(
                WorkflowCpnClosureCorrelationIssue(
                    WorkflowCpnClosureCorrelationIssueCode.EXPORT_PLAN_MISMATCH,
                    ("plan", "identity"),
                )
            )
        if (
            correlation_input.export.execution_plan_identity
            != correlation_input.plan_identity
        ):
            issues.append(
                WorkflowCpnClosureCorrelationIssue(
                    WorkflowCpnClosureCorrelationIssueCode.EXPORT_PLAN_MISMATCH,
                    ("export", "execution_plan_identity"),
                )
            )
        if (
            correlation_input.export.cpn_execution_profile_identity
            != correlation_input.profile_identity
        ):
            issues.append(
                WorkflowCpnClosureCorrelationIssue(
                    WorkflowCpnClosureCorrelationIssueCode.EXPORT_PROFILE_MISMATCH,
                    ("export", "cpn_execution_profile_identity"),
                )
            )
        if (
            correlation_input.plan.child_interface
            != correlation_input.export.interface
        ):
            issues.append(
                WorkflowCpnClosureCorrelationIssue(
                    WorkflowCpnClosureCorrelationIssueCode.EXPORT_INTERFACE_MISMATCH,
                    ("export", "interface"),
                )
            )
        if (
            correlation_input.export.nominal_definition_identity
            != correlation_input.plan.nominal_definition_identity.value
            or correlation_input.export.canonical_definition_identity
            != correlation_input.plan.canonical_definition_identity.value
            or correlation_input.export.canonical_definition_representation_profile_identity
            != correlation_input.plan.canonical_definition_representation_profile_identity
            or correlation_input.export.canonical_definition_sha256
            != correlation_input.plan.canonical_definition_sha256
        ):
            issues.append(
                WorkflowCpnClosureCorrelationIssue(
                    WorkflowCpnClosureCorrelationIssueCode.EXPORT_DEFINITION_MISMATCH,
                    ("export", "definition"),
                )
            )
        return WorkflowCpnClosureCorrelationResult(tuple(issues))
