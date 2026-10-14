"""Reviewed local CPN execution-profile construction and resolution."""

from dataclasses import dataclass
from typing import final

from ..firing import transitions as firing_transitions
from .definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
    WorkflowCpnExecutionProfileResolutionIssue,
    WorkflowCpnExecutionProfileResolutionResult,
    WorkflowCpnExecutionProfileResolverIdentity,
)
from .building import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)


@dataclass(frozen=True, slots=True)
class WorkflowCpnExecutionProfileResolutionRequest:
    """One complete retained profile requested for local resolution."""

    profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.profile) is not WorkflowCpnExecutionProfile:
            raise TypeError("profile must be WorkflowCpnExecutionProfile")


@final
class WorkflowCpnExecutionProfileResolver:
    """Resolve every retained profile component against local operations."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowCpnExecutionProfileResolverIdentity:
        """Return exact profile-resolution semantics identity."""
        return WorkflowCpnExecutionProfileResolverIdentity()

    def execute(
        self, request: WorkflowCpnExecutionProfileResolutionRequest
    ) -> WorkflowCpnExecutionProfileResolutionResult:
        """Return all unavailable components without resolving by name lookup."""
        if type(request) is not WorkflowCpnExecutionProfileResolutionRequest:
            raise TypeError(
                "request must be WorkflowCpnExecutionProfileResolutionRequest"
            )
        profile = request.profile
        supported = WorkflowCpnExecutionProfileBuilder().execute(
            WorkflowCpnExecutionProfileBuildingRequest()
        )
        issues = tuple(
            WorkflowCpnExecutionProfileResolutionIssue(
                name,
                getattr(profile, name),
                getattr(supported, name),
            )
            for name in sorted(profile.__dataclass_fields__)
            if getattr(profile, name) != getattr(supported, name)
        )
        profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
            WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
        )
        return WorkflowCpnExecutionProfileResolutionResult(
            profile_identity,
            issues,
            None if issues else firing_transitions.CpnTransitionFirer(),
        )
