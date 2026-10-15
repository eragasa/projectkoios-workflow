"""Verification of canonical in-memory pure CPN transcript refiring."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from _pure_action_fixtures import _commit_fixture
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionEncoder,
    ExperimentalWorkflowCpnMarkingDecoder,
    ExperimentalWorkflowCpnMarkingEncoder,
)
from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCpnReplayBundleFactory,
    ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec,
    ExperimentalWorkflowPureActionCpnReplayService,
    ExperimentalWorkflowPureActionCpnReplayStatus,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingSelector,
    ColoredPetriNetFiringResultIdentity,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetSelectionDirective,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetTransitionEnabler,
    ColoredPetriNetTransitionFirer,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)


def _bundle_and_bytes():  # type: ignore[no-untyped-def]
    fixture = _commit_fixture()
    assert fixture.invocation_fixture.cpn_plan is not None
    assert fixture.firing.firing_result is not None
    bundle = ExperimentalWorkflowPureActionCpnReplayBundleFactory().execute(
        cpn_plan=fixture.invocation_fixture.cpn_plan,
        firing_result=fixture.firing.firing_result,
    )
    encoded = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
        bundle
    )
    return fixture, bundle, encoded


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def test_bundle_codec_and_service_refire_exact_success_without_owner() -> None:
    fixture, bundle, encoded = _bundle_and_bytes()
    owner_calls = fixture.invocation_fixture.firer.calls
    codec = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec()

    assert codec.decode(encoded) == bundle
    result = ExperimentalWorkflowPureActionCpnReplayService().execute(encoded)

    assert (
        result.status is ExperimentalWorkflowPureActionCpnReplayStatus.REPLAYED
    )
    assert result.bundle_identity == bundle.identity
    assert bundle.identity.value == (
        "60ca7e19c47bc8026f178fb97a79f9f9fd8348d38e3f6a1118dc71229ae3d5da"
    )
    assert result.bundle_sha256 == (
        "d001410c1f5888d2d31d4a8a81960cbb571b3064d9f51cc9f491be20f0c4b7e4"
    )
    assert result.firing_result == fixture.firing.firing_result
    assert fixture.invocation_fixture.firer.calls == owner_calls
    assert codec.encode(codec.decode(encoded)) == encoded


def test_replay_reconstructs_retained_directed_selection() -> None:
    fixture, _, _ = _bundle_and_bytes()
    plan = fixture.invocation_fixture.cpn_plan
    original = fixture.firing.firing_result
    assert plan is not None
    assert original is not None
    firing_input = original.firing_input
    definition = replace(
        firing_input.definition,
        selection_policy=ColoredPetriNetSelectionPolicy.DIRECTED_ALLOWED,
    )
    enablement = ColoredPetriNetTransitionEnabler().execute(
        definition,
        firing_input.predecessor_marking,
    )
    assert enablement.enabled_bindings
    directive = ColoredPetriNetSelectionDirective(
        enablement.identity,
        enablement.enabled_bindings[0],
    )
    selection = ColoredPetriNetBindingSelector().execute(
        definition,
        enablement,
        directive,
    )
    directed_input = replace(
        firing_input,
        definition=definition,
        enablement_result=enablement,
        selection_result=selection,
        selected_binding=directive.binding,
        directive_identity=directive.identity,
    )
    directed_result = ColoredPetriNetTransitionFirer().execute(directed_input)
    directed_plan = replace(
        plan,
        definition_bytes=ExperimentalWorkflowCpnDefinitionEncoder().encode(
            definition
        ),
    )
    bundle = ExperimentalWorkflowPureActionCpnReplayBundleFactory().execute(
        cpn_plan=directed_plan,
        firing_result=directed_result,
    )
    encoded = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
        bundle
    )

    replayed = ExperimentalWorkflowPureActionCpnReplayService().execute(encoded)

    assert (
        replayed.status
        is ExperimentalWorkflowPureActionCpnReplayStatus.REPLAYED
    )
    assert replayed.firing_result == directed_result


def test_replay_rejects_changed_expected_result_identity() -> None:
    _, bundle, _ = _bundle_and_bytes()
    changed = replace(
        bundle,
        expected_firing_result_identity=ColoredPetriNetFiringResultIdentity(
            "0" * 64
        ),
    )
    encoded = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
        changed
    )

    result = ExperimentalWorkflowPureActionCpnReplayService().execute(encoded)

    assert (
        result.status is ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT
    )
    assert result.diagnostics == (
        "pure CPN refiring differs from retained result",
    )


def test_replay_rejects_changed_external_output_binding() -> None:
    _, bundle, _ = _bundle_and_bytes()
    assignment = bundle.external_output_binding.assignments[0]
    changed_binding = replace(
        bundle.external_output_binding,
        assignments=(
            replace(
                assignment,
                value=ColoredPetriNetValue(
                    ColoredPetriNetValueKind.STRING,
                    "substituted.artifact-set",
                ),
            ),
        ),
    )
    changed = replace(bundle, external_output_binding=changed_binding)
    encoded = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
        changed
    )

    result = ExperimentalWorkflowPureActionCpnReplayService().execute(encoded)

    assert (
        result.status is ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT
    )


def test_replay_rejects_changed_successor_body() -> None:
    _, bundle, _ = _bundle_and_bytes()
    decoder = ExperimentalWorkflowCpnMarkingDecoder()
    encoder = ExperimentalWorkflowCpnMarkingEncoder()
    successor = decoder.decode(bundle.successor_marking_bytes)
    changed_successor = replace(
        successor,
        identity=ColoredPetriNetMarkingIdentity("changed.successor"),
    )
    changed = replace(
        bundle,
        successor_marking_bytes=encoder.encode(changed_successor),
    )
    encoded = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
        changed
    )

    result = ExperimentalWorkflowPureActionCpnReplayService().execute(encoded)

    assert (
        result.status is ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT
    )


def test_replay_preserves_unsupported_profile_as_incompatible() -> None:
    fixture, bundle, _ = _bundle_and_bytes()
    assert fixture.invocation_fixture.cpn_plan is not None
    changed_profile = replace(
        bundle.execution_profile,
        transition_firer_identity="unsupported-transition-firer",
    )
    changed_plan = replace(
        fixture.invocation_fixture.cpn_plan,
        execution_profile=changed_profile,
    )
    changed = replace(
        bundle,
        cpn_plan_identity=changed_plan.identity,
        execution_profile=changed_profile,
    )
    encoded = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().encode(
        changed
    )

    result = ExperimentalWorkflowPureActionCpnReplayService().execute(encoded)

    assert (
        result.status
        is ExperimentalWorkflowPureActionCpnReplayStatus.INCOMPATIBLE
    )
    assert result.diagnostics == ("CPN execution profile is unsupported",)


def test_bundle_rejects_execution_profile_substitution_under_same_plan() -> (
    None
):
    _, bundle, _ = _bundle_and_bytes()
    changed_profile = replace(
        bundle.execution_profile,
        transition_firer_identity="substituted-transition-firer",
    )

    with pytest.raises(ValueError, match="CPN plan identity differs"):
        replace(bundle, execution_profile=changed_profile)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda document: document | {"unknown": True},
        lambda document: document | {"schema": "unsupported"},
        lambda document: (
            document
            | {
                "bundle": document["bundle"]
                | {"definition_bytes_base64": "***"}
            }
        ),
        lambda document: (
            document
            | {"bundle": document["bundle"] | {"bundle_identity": "0" * 64}}
        ),
    ),
)
def test_bundle_decoder_rejects_changed_closed_state(mutation: object) -> None:
    _, _, encoded = _bundle_and_bytes()
    document = json.loads(encoded)
    assert callable(mutation)

    with pytest.raises(ValueError):
        ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().decode(
            _canonical(mutation(document))
        )


def test_service_classifies_invalid_transcripts_as_corrupt() -> None:
    _, _, encoded = _bundle_and_bytes()
    service = ExperimentalWorkflowPureActionCpnReplayService()

    whitespace = service.execute(b" " + encoded)
    wrong_type = service.execute("{}")  # type: ignore[arg-type]

    assert (
        whitespace.status
        is ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT
    )
    assert (
        wrong_type.status
        is ExperimentalWorkflowPureActionCpnReplayStatus.CORRUPT
    )
