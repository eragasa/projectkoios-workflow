"""Private canonical firing-result replay transport fixtures."""

from _firing_fixtures import valid_firing_input

from dataclasses import replace

from projectkoios.workflow.petrinet.colored.canonical.firings import (
    CpnCanonicalFiringResult,
    CpnCanonicalFiringResultCodec,
    CpnCanonicalFiringResultEncodingInput,
)
from projectkoios.workflow.petrinet.colored.firing.outcomes import (
    CpnFiringResult,
)
from projectkoios.workflow.petrinet.colored.firing.transitions import (
    CpnTransitionFirer,
)
from projectkoios.workflow.petrinet.colored.profiles.defaults import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
    WorkflowCpnExecutionProfileResolutionRequest,
    WorkflowCpnExecutionProfileResolver,
)
from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileResolutionResult,
)
from projectkoios.workflow.petrinet.colored.selection import (
    CpnSelectionDirectiveIdentity,
)


def firing_result() -> CpnFiringResult:
    """Return one successful pure firing result."""
    return CpnTransitionFirer().execute(valid_firing_input())


def failed_firing_result() -> CpnFiringResult:
    """Return one structured directive-correlation firing failure."""
    firing_input = replace(
        valid_firing_input(),
        directive_identity=CpnSelectionDirectiveIdentity("a" * 64),
    )
    return CpnTransitionFirer().execute(firing_input)


def execution_profile() -> WorkflowCpnExecutionProfile:
    """Return the exact retained profile governing replay."""
    return WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )


def profile_resolution() -> WorkflowCpnExecutionProfileResolutionResult:
    """Return exact local operation resolution for the retained profile."""
    return WorkflowCpnExecutionProfileResolver().execute(
        WorkflowCpnExecutionProfileResolutionRequest(execution_profile())
    )


def canonical_firing_result() -> CpnCanonicalFiringResult:
    """Return exact canonical replay bytes for the firing result."""
    return CpnCanonicalFiringResultCodec().encode(
        CpnCanonicalFiringResultEncodingInput(
            firing_result(), execution_profile()
        )
    )
