"""Direct tests for canonical shadow firing and replay correlations."""

from dataclasses import replace

import pytest
from _firing_fixtures import valid_firing_input

from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionEncodingInput,
)
from projectkoios.workflow.petrinet.colored.canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingEncodingInput,
)
from projectkoios.workflow.petrinet.colored.markings import CpnMarkingIdentity
from projectkoios.workflow.petrinet.colored.profiles.building import (
    WorkflowCpnExecutionProfileBuilder,
    WorkflowCpnExecutionProfileBuildingRequest,
)
from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFiringError,
    CpnShadowFiringErrorCode,
    CpnShadowFiringInput,
)
from projectkoios.workflow.petrinet.colored.shadow.firing import CpnShadowFirer


def shadow_input() -> CpnShadowFiringInput:
    firing_input = valid_firing_input()
    definition = CpnCanonicalDefinitionCodec().encode(
        CpnCanonicalDefinitionEncodingInput(firing_input.definition)
    )
    predecessor = CpnCanonicalMarkingCodec().encode(
        CpnCanonicalMarkingEncodingInput(firing_input.predecessor_marking)
    )
    profile = WorkflowCpnExecutionProfileBuilder().execute(
        WorkflowCpnExecutionProfileBuildingRequest()
    )
    return CpnShadowFiringInput(definition, profile, predecessor, firing_input)


def test_execute__binds_definition_profile_markings_and_firing_result() -> None:
    first = CpnShadowFirer().execute(shadow_input())
    replay = CpnShadowFirer().execute(shadow_input())
    assert first == replay
    assert first.firing_result_identity == first.firing_result.identity
    assert first.successor_marking_identity is not None
    assert first.successor_marking_sha256 is not None


def test_execute__rejects_unresolved_retained_profile() -> None:
    admitted = shadow_input()
    changed_profile = replace(
        admitted.execution_profile,
        expression_evaluator_identity="unavailable-evaluator",
    )
    with pytest.raises(CpnShadowFiringError) as captured:
        CpnShadowFirer().execute(
            replace(admitted, execution_profile=changed_profile)
        )
    assert (
        captured.value.code
        is CpnShadowFiringErrorCode.EXECUTION_PROFILE_UNAVAILABLE
    )


def test_execute__rejects_predecessor_byte_mismatch() -> None:
    admitted = shadow_input()
    changed_marking = replace(
        admitted.firing_input.predecessor_marking,
        identity=CpnMarkingIdentity("changed"),
    )
    changed_input = replace(
        admitted.firing_input, predecessor_marking=changed_marking
    )
    with pytest.raises(CpnShadowFiringError) as captured:
        CpnShadowFirer().execute(replace(admitted, firing_input=changed_input))
    assert (
        captured.value.code
        is CpnShadowFiringErrorCode.PREDECESSOR_MARKING_MISMATCH
    )
