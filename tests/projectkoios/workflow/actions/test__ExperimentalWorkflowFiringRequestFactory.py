from __future__ import annotations

import hashlib
import inspect

import pytest
from projectkoios.workflow.actions import (
    ExperimentalWorkflowFiringRequestCoordinates,
    ExperimentalWorkflowFiringRequestFactory,
    ExperimentalWorkflowSelectedBindingEncoder,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowFiringRequest,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
    WorkflowPayloadCodecIdentity,
    WorkflowPayloadOwnerIdentity,
    WorkflowPayloadRepresentationIdentity,
    WorkflowPayloadSchemaIdentity,
    WorkflowPayloadTypeIdentity,
    WorkflowTransitionIdentity,
)
from projectkoios.workflow_sdk.payloads import (
    WorkflowInlinePayload,
    WorkflowPayloadContract,
)
from projectkoios.workflow_sdk.serialization import (
    WorkflowFiringRequestJsonCodec,
)


def _contract(role: str, maximum: int = 128) -> WorkflowPayloadContract:
    return WorkflowPayloadContract(
        role=role,
        owner_identity=WorkflowPayloadOwnerIdentity("fixture.owner"),
        payload_type_identity=WorkflowPayloadTypeIdentity(f"fixture.{role}"),
        schema_identity=WorkflowPayloadSchemaIdentity(f"fixture.{role}:1"),
        codec_identity=WorkflowPayloadCodecIdentity(f"fixture.{role}-json:1"),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            "canonical-json:1"
        ),
        media_type=f"application/vnd.fixture.{role}.v1+json",
        maximum_byte_length=maximum,
    )


def _descriptor() -> WorkflowFirerDescriptor:
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity("fixture.firer"),
        implementation_identity=WorkflowFirerImplementationIdentity(
            "fixture.firer:1"
        ),
        input_contracts=(_contract("projection_request"),),
        output_contracts=(_contract("artifact_set_identity", 256),),
        evidence_contracts=(_contract("artifact_set", 1024),),
        bounds=WorkflowFiringBounds(
            maximum_input_count=1,
            maximum_output_count=1,
            maximum_evidence_count=1,
            maximum_input_bytes=128,
            maximum_output_bytes=256,
            maximum_total_bytes=1280,
            maximum_reason_count=1,
        ),
    )


def _transition_binding(
    descriptor: WorkflowFirerDescriptor,
) -> WorkflowTransitionFirerBinding:
    return WorkflowTransitionFirerBinding(
        definition_identity=WorkflowDefinitionIdentity("fixture.definition"),
        transition_identity=WorkflowTransitionIdentity("fixture.transition"),
        firer_identity=descriptor.identity,
        input_roles=("projection_request",),
        output_roles=("artifact_set_identity",),
        binding_version="fixture.1",
    )


def _selected_binding(
    *,
    count: int = 7,
    label_kind: ColoredPetriNetValueKind = ColoredPetriNetValueKind.STRING,
    label: str | int = "alpha",
    reverse: bool = False,
) -> ColoredPetriNetBinding:
    assignments = (
        ColoredPetriNetBindingAssignment(
            variable_identity=ColoredPetriNetBindingVariableIdentity("count"),
            value=ColoredPetriNetValue(
                kind=ColoredPetriNetValueKind.INTEGER,
                value=count,
            ),
        ),
        ColoredPetriNetBindingAssignment(
            variable_identity=ColoredPetriNetBindingVariableIdentity("label"),
            value=ColoredPetriNetValue(kind=label_kind, value=label),
        ),
    )
    return ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity(
            "fixture.transition"
        ),
        assignments=tuple(reversed(assignments)) if reverse else assignments,
    )


def _coordinates(
    predecessor_revision: int = 7,
) -> ExperimentalWorkflowFiringRequestCoordinates:
    return ExperimentalWorkflowFiringRequestCoordinates(
        net_instance_identity=WorkflowNetInstanceIdentity("fixture.net"),
        predecessor_marking_identity=WorkflowMarkingIdentity("fixture.marking"),
        predecessor_revision=predecessor_revision,
        occurrence_identity=WorkflowOccurrenceIdentity("fixture.occurrence"),
        attempt_identity=WorkflowAttemptIdentity("fixture.attempt"),
        attempt_ordinal=0,
    )


def _input(
    contract: WorkflowPayloadContract,
    *,
    role: str | None = None,
    codec_identity: WorkflowPayloadCodecIdentity | None = None,
    payload: bytes = b"{}",
) -> WorkflowInlinePayload:
    return WorkflowInlinePayload(
        role=role or contract.role,
        owner_identity=contract.owner_identity,
        payload_type_identity=contract.payload_type_identity,
        schema_identity=contract.schema_identity,
        codec_identity=codec_identity or contract.codec_identity,
        representation_identity=contract.representation_identity,
        media_type=contract.media_type,
        payload=payload,
        byte_length=len(payload),
        payload_sha256=hashlib.sha256(payload).hexdigest(),
    )


def _factory_request(
    *,
    selected_binding: ColoredPetriNetBinding | None = None,
    coordinates: ExperimentalWorkflowFiringRequestCoordinates | None = None,
    inputs: tuple[WorkflowInlinePayload, ...] | None = None,
) -> WorkflowFiringRequest:
    descriptor = _descriptor()
    transition_binding = _transition_binding(descriptor)
    return ExperimentalWorkflowFiringRequestFactory().execute(
        transition_binding=transition_binding,
        firer_descriptor=descriptor,
        selected_binding=selected_binding or _selected_binding(),
        coordinates=coordinates or _coordinates(),
        inputs=(
            inputs
            if inputs is not None
            else (_input(descriptor.input_contracts[0]),)
        ),
    )


def test_selected_binding_encoder_is_exact_ordered_and_type_tagged() -> None:
    encoder = ExperimentalWorkflowSelectedBindingEncoder()
    binding = _selected_binding()

    payload = encoder.encode(binding)

    assert payload == (
        b'{"assignments":[{"kind":"integer","value":"7",'
        b'"variable_identity":"count"},{"kind":"string","value":"alpha",'
        b'"variable_identity":"label"}],"schema_identity":'
        b'"projectkoios.workflow.experimental-selected-binding:1",'
        b'"transition_identity":"fixture.transition"}'
    )
    assert encoder.sha256(binding) == hashlib.sha256(payload).hexdigest()
    assert encoder.profile_identity == (
        "projectkoios.workflow.experimental-selected-binding-canonical-json:1"
    )


def test_selected_binding_digest_changes_with_order_kind_or_value() -> None:
    encoder = ExperimentalWorkflowSelectedBindingEncoder()
    original = encoder.sha256(_selected_binding())

    assert encoder.sha256(_selected_binding(reverse=True)) != original
    assert encoder.sha256(_selected_binding(count=8)) != original
    assert (
        encoder.sha256(
            _selected_binding(
                label_kind=ColoredPetriNetValueKind.INTEGER,
                label=1,
            )
        )
        != original
    )


def test_factory_derives_context_digest_and_canonical_sdk_request() -> None:
    selected_binding = _selected_binding()
    request = _factory_request(selected_binding=selected_binding)

    assert request.context.selected_binding_sha256 == (
        ExperimentalWorkflowSelectedBindingEncoder().sha256(selected_binding)
    )
    assert request.context.definition_identity.value == "fixture.definition"
    assert request.context.transition_identity.value == "fixture.transition"
    assert (
        request.binding_identity == _transition_binding(_descriptor()).identity
    )
    codec = WorkflowFiringRequestJsonCodec()
    assert codec.decode(codec.encode(request)) == request
    assert (
        "selected_binding_sha256"
        not in inspect.signature(
            ExperimentalWorkflowFiringRequestFactory.execute
        ).parameters
    )


def test_factory_rejects_selected_binding_for_another_transition() -> None:
    selected = _selected_binding()
    wrong = ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity("other"),
        assignments=selected.assignments,
    )

    with pytest.raises(ValueError, match="wrong transition"):
        _factory_request(selected_binding=wrong)


def test_factory_rejects_wrong_input_role_codec_or_bound() -> None:
    descriptor = _descriptor()
    contract = descriptor.input_contracts[0]
    wrong_codec = WorkflowPayloadCodecIdentity("fixture.wrong-codec:1")
    for value in (
        _input(contract, role="wrong_role"),
        _input(contract, codec_identity=wrong_codec),
    ):
        with pytest.raises(ValueError, match="metadata differs"):
            _factory_request(inputs=(value,))

    with pytest.raises(ValueError, match="contract byte bound"):
        _factory_request(inputs=(_input(contract, payload=b"x" * 129),))


def test_predecessor_change_cannot_reuse_the_same_request_identity() -> None:
    selected = _selected_binding()
    first = _factory_request(
        selected_binding=selected,
        coordinates=_coordinates(predecessor_revision=7),
    )
    stale = _factory_request(
        selected_binding=selected,
        coordinates=_coordinates(predecessor_revision=8),
    )

    assert first.context.selected_binding_sha256 == (
        stale.context.selected_binding_sha256
    )
    assert first.context.predecessor_revision == 7
    assert stale.context.predecessor_revision == 8
    assert first.identity != stale.identity


def test_encoder_rejects_oversized_values_and_identities() -> None:
    oversized_string = ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity(
            "fixture.transition"
        ),
        assignments=(
            ColoredPetriNetBindingAssignment(
                variable_identity=ColoredPetriNetBindingVariableIdentity(
                    "value"
                ),
                value=ColoredPetriNetValue(
                    ColoredPetriNetValueKind.STRING,
                    "x" * 4097,
                ),
            ),
        ),
    )
    oversized_identity = ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity("x" * 513),
        assignments=(),
    )

    encoder = ExperimentalWorkflowSelectedBindingEncoder()
    with pytest.raises(ValueError, match="4096 UTF-8 bytes"):
        encoder.encode(oversized_string)
    with pytest.raises(ValueError, match="512 UTF-8 bytes"):
        encoder.encode(oversized_identity)


def test_factory_and_encoder_are_non_subclassable() -> None:
    with pytest.raises(TypeError, match="not subclassable"):

        class _InvalidFactory(ExperimentalWorkflowFiringRequestFactory):
            pass

    with pytest.raises(TypeError, match="not subclassable"):

        class _InvalidEncoder(ExperimentalWorkflowSelectedBindingEncoder):
            pass
