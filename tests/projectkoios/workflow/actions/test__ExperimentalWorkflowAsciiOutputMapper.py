from __future__ import annotations

import hashlib
import inspect
from dataclasses import replace

import pytest
from projectkoios.workflow.actions import (
    ExperimentalWorkflowAsciiOutputMapper,
    ExperimentalWorkflowAsciiOutputMappingDescriptor,
    ExperimentalWorkflowMappedActionResult,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowFiringRejected,
    WorkflowFiringRequest,
    WorkflowFiringSucceeded,
    WorkflowOccurrenceContext,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowFiringRequestIdentity,
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

_EXTERNAL_VARIABLE = ColoredPetriNetBindingVariableIdentity(
    "artifact_set_identity"
)
_OWNER_IDENTITY_TEXT = "fixture.saved-state-semantic-identity:1:" + "a" * 64


def _contract(
    role: str,
    *,
    representation: str,
    maximum: int,
) -> WorkflowPayloadContract:
    return WorkflowPayloadContract(
        role=role,
        owner_identity=WorkflowPayloadOwnerIdentity("fixture.owner"),
        payload_type_identity=WorkflowPayloadTypeIdentity(f"fixture.{role}"),
        schema_identity=WorkflowPayloadSchemaIdentity(f"fixture.{role}:1"),
        codec_identity=WorkflowPayloadCodecIdentity(f"fixture.{role}-codec:1"),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            representation
        ),
        media_type=f"application/vnd.fixture.{role}.v1+octet-stream",
        maximum_byte_length=maximum,
    )


def _descriptor(
    *,
    output_contract: WorkflowPayloadContract | None = None,
    evidence_contracts: tuple[WorkflowPayloadContract, ...] | None = None,
) -> WorkflowFirerDescriptor:
    request_contract = _contract(
        "projection_request",
        representation="canonical-json:1",
        maximum=128,
    )
    selected_output = output_contract or _contract(
        "artifact_set_identity",
        representation="canonical-ascii:1",
        maximum=256,
    )
    selected_evidence = (
        evidence_contracts
        if evidence_contracts is not None
        else (
            _contract(
                "artifact_set",
                representation="canonical-json:1",
                maximum=1024,
            ),
        )
    )
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity("fixture.project-artifact-set"),
        implementation_identity=WorkflowFirerImplementationIdentity(
            "fixture.project-artifact-set:1"
        ),
        input_contracts=(request_contract,),
        output_contracts=(selected_output,),
        evidence_contracts=selected_evidence,
        bounds=WorkflowFiringBounds(
            maximum_input_count=1,
            maximum_output_count=1,
            maximum_evidence_count=len(selected_evidence),
            maximum_input_bytes=128,
            maximum_output_bytes=selected_output.maximum_byte_length,
            maximum_total_bytes=(
                selected_output.maximum_byte_length
                + sum(item.maximum_byte_length for item in selected_evidence)
            ),
            maximum_reason_count=1,
        ),
    )


def _transition_binding(
    descriptor: WorkflowFirerDescriptor,
    *,
    output_roles: tuple[str, ...] | None = None,
) -> WorkflowTransitionFirerBinding:
    return WorkflowTransitionFirerBinding(
        definition_identity=WorkflowDefinitionIdentity("fixture.definition"),
        transition_identity=WorkflowTransitionIdentity("fixture.transition"),
        firer_identity=descriptor.identity,
        input_roles=tuple(item.role for item in descriptor.input_contracts),
        output_roles=(
            output_roles
            if output_roles is not None
            else tuple(item.role for item in descriptor.output_contracts)
        ),
        binding_version="fixture.1",
    )


def _mapping(
    *,
    descriptor: WorkflowFirerDescriptor | None = None,
) -> ExperimentalWorkflowAsciiOutputMappingDescriptor:
    selected_descriptor = descriptor or _descriptor()
    return ExperimentalWorkflowAsciiOutputMappingDescriptor(
        transition_binding=_transition_binding(selected_descriptor),
        firer_descriptor=selected_descriptor,
        output_role="artifact_set_identity",
        external_variable_identity=_EXTERNAL_VARIABLE,
        external_value_kind=ColoredPetriNetValueKind.STRING,
        mapping_version="fixture.1",
    )


def _context(
    *,
    predecessor_revision: int = 7,
    selected_binding_sha256: str = "b" * 64,
) -> WorkflowOccurrenceContext:
    return WorkflowOccurrenceContext(
        definition_identity=WorkflowDefinitionIdentity("fixture.definition"),
        net_instance_identity=WorkflowNetInstanceIdentity("fixture.net"),
        transition_identity=WorkflowTransitionIdentity("fixture.transition"),
        predecessor_marking_identity=WorkflowMarkingIdentity("fixture.marking"),
        predecessor_revision=predecessor_revision,
        selected_binding_sha256=selected_binding_sha256,
        occurrence_identity=WorkflowOccurrenceIdentity("fixture.occurrence"),
        attempt_identity=WorkflowAttemptIdentity("fixture.attempt"),
        attempt_ordinal=0,
    )


def _inline(
    contract: WorkflowPayloadContract,
    payload: bytes,
    *,
    role: str | None = None,
    codec_identity: WorkflowPayloadCodecIdentity | None = None,
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


def _request(
    mapping: ExperimentalWorkflowAsciiOutputMappingDescriptor,
    *,
    context: WorkflowOccurrenceContext | None = None,
) -> WorkflowFiringRequest:
    descriptor = mapping.firer_descriptor
    return WorkflowFiringRequest(
        context=context or _context(),
        binding_identity=mapping.transition_binding.identity,
        firer_identity=descriptor.identity,
        inputs=(_inline(descriptor.input_contracts[0], b"{}"),),
    )


def _result(
    mapping: ExperimentalWorkflowAsciiOutputMappingDescriptor,
    request: WorkflowFiringRequest,
    *,
    output_payload: bytes = _OWNER_IDENTITY_TEXT.encode("ascii"),
    output_role: str | None = None,
    output_codec: WorkflowPayloadCodecIdentity | None = None,
    include_evidence: bool = True,
    output: WorkflowInlinePayload | None = None,
) -> WorkflowFiringSucceeded:
    descriptor = mapping.firer_descriptor
    selected_output = output or _inline(
        descriptor.output_contracts[0],
        output_payload,
        role=output_role,
        codec_identity=output_codec,
    )
    evidence = (
        (_inline(descriptor.evidence_contracts[0], b'{"artifact_count":4}'),)
        if include_evidence
        else ()
    )
    return WorkflowFiringSucceeded(
        request_identity=request.identity,
        occurrence_identity=request.context.occurrence_identity,
        attempt_identity=request.context.attempt_identity,
        firer_identity=request.firer_identity,
        outputs=(selected_output,),
        evidence=evidence,
    )


def _transition(
    variable: ColoredPetriNetBindingVariableIdentity = _EXTERNAL_VARIABLE,
) -> ColoredPetriNetTransitionDefinition:
    return ColoredPetriNetTransitionDefinition(
        identity=ColoredPetriNetTransitionIdentity("fixture.transition"),
        input_variable_identities=(),
        external_output_variable_identities=(variable,),
        guard=ColoredPetriNetGuardExpression(ColoredPetriNetGuardOperator.TRUE),
    )


def _execute(
    mapping: ExperimentalWorkflowAsciiOutputMappingDescriptor,
    request: WorkflowFiringRequest,
    result: WorkflowFiringSucceeded,
    *,
    transition: ColoredPetriNetTransitionDefinition | None = None,
    expected_context: WorkflowOccurrenceContext | None = None,
) -> ExperimentalWorkflowMappedActionResult:
    return ExperimentalWorkflowAsciiOutputMapper().execute(
        mapping=mapping,
        transition=transition or _transition(),
        expected_context=expected_context or request.context,
        request=request,
        result=result,
    )


def test_descriptor_content_identity_closes_exact_sdk_contracts() -> None:
    mapping = _mapping()

    assert len(mapping.identity.value) == 64
    assert mapping.output_contract.role == "artifact_set_identity"
    assert tuple(item.role for item in mapping.evidence_contracts) == (
        "artifact_set",
    )
    assert (
        replace(mapping, mapping_version="fixture.2").identity
        != mapping.identity
    )
    assert (
        replace(
            mapping,
            external_variable_identity=ColoredPetriNetBindingVariableIdentity(
                "other"
            ),
        ).identity
        != mapping.identity
    )


def test_descriptor_rejects_invalid_output_contract_or_role() -> None:
    for representation, maximum, message in (
        ("canonical-json:1", 256, "not canonical ASCII"),
        ("canonical-ascii:1", 513, "exceeds 512"),
    ):
        descriptor = _descriptor(
            output_contract=_contract(
                "artifact_set_identity",
                representation=representation,
                maximum=maximum,
            )
        )
        with pytest.raises(ValueError, match=message):
            _mapping(descriptor=descriptor)

    descriptor = _descriptor()
    with pytest.raises(ValueError, match="output roles differ"):
        ExperimentalWorkflowAsciiOutputMappingDescriptor(
            transition_binding=_transition_binding(
                descriptor,
                output_roles=("wrong_role",),
            ),
            firer_descriptor=descriptor,
            output_role="artifact_set_identity",
            external_variable_identity=_EXTERNAL_VARIABLE,
            external_value_kind=ColoredPetriNetValueKind.STRING,
            mapping_version="fixture.1",
        )


def test_mapper_maps_string_and_retains_separate_evidence() -> None:
    mapping = _mapping()
    request = _request(mapping)
    result = _result(mapping, request)

    mapped = _execute(mapping, request, result)

    assignment = mapped.external_output_binding.assignments[0]
    assert mapped.mapping_identity == mapping.identity
    assert mapped.request_identity == request.identity
    assert mapped.result_identity == result.identity
    assert mapped.external_output_binding.transition_identity.value == (
        "fixture.transition"
    )
    assert assignment.variable_identity == _EXTERNAL_VARIABLE
    assert assignment.value.kind is ColoredPetriNetValueKind.STRING
    assert assignment.value.value == _OWNER_IDENTITY_TEXT
    assert mapped.source_output == result.outputs[0]
    assert mapped.evidence == result.evidence
    assert assignment.value.value != mapped.source_output.payload_sha256
    assert assignment.value.value != mapped.evidence[0].payload_sha256
    assert _execute(mapping, request, result).identity == mapped.identity


@pytest.mark.parametrize(
    "payload",
    [
        b"identity with space",
        b"identity\n",
        b"\xc3\xa9",
        b"/private/artifact",
        b"file:private-artifact",
        b"x" * 257,
    ],
)
def test_mapper_rejects_malformed_or_overbound_identity_bytes(
    payload: bytes,
) -> None:
    mapping = _mapping()
    request = _request(mapping)

    with pytest.raises(ValueError):
        _execute(
            mapping, request, _result(mapping, request, output_payload=payload)
        )


def test_mapper_rejects_stale_context_and_result_correlation() -> None:
    mapping = _mapping()
    request = _request(mapping)
    result = _result(mapping, request)

    for stale_context in (
        _context(predecessor_revision=8),
        _context(selected_binding_sha256="d" * 64),
    ):
        with pytest.raises(ValueError, match="retained expectation"):
            _execute(
                mapping,
                request,
                result,
                expected_context=stale_context,
            )

    wrong_result = WorkflowFiringSucceeded(
        request_identity=WorkflowFiringRequestIdentity("c" * 64),
        occurrence_identity=request.context.occurrence_identity,
        attempt_identity=request.context.attempt_identity,
        firer_identity=request.firer_identity,
        outputs=result.outputs,
        evidence=result.evidence,
    )
    with pytest.raises(ValueError, match="request identity differs"):
        _execute(mapping, request, wrong_result)


def test_mapper_rejects_wrong_output_metadata_or_missing_evidence() -> None:
    mapping = _mapping()
    request = _request(mapping)

    wrong_codec = WorkflowPayloadCodecIdentity("fixture.wrong-codec:1")
    for result in (
        _result(mapping, request, output_role="wrong_role"),
        _result(mapping, request, output_codec=wrong_codec),
    ):
        with pytest.raises(ValueError, match="metadata differs"):
            _execute(mapping, request, result)

    with pytest.raises(ValueError, match="exactly satisfy"):
        _execute(
            mapping,
            request,
            _result(mapping, request, include_evidence=False),
        )


def test_mapper_rejects_reordered_evidence_contracts() -> None:
    first = _contract(
        "artifact_set",
        representation="canonical-json:1",
        maximum=1024,
    )
    second = _contract(
        "projection_trace",
        representation="canonical-json:1",
        maximum=1024,
    )
    mapping = _mapping(
        descriptor=_descriptor(evidence_contracts=(first, second))
    )
    request = _request(mapping)
    output = _inline(
        mapping.output_contract,
        _OWNER_IDENTITY_TEXT.encode("ascii"),
    )
    result = WorkflowFiringSucceeded(
        request_identity=request.identity,
        occurrence_identity=request.context.occurrence_identity,
        attempt_identity=request.context.attempt_identity,
        firer_identity=request.firer_identity,
        outputs=(output,),
        evidence=(
            _inline(second, b'{"trace":1}'),
            _inline(first, b'{"artifact_count":4}'),
        ),
    )

    with pytest.raises(ValueError, match="metadata differs"):
        _execute(mapping, request, result)


def test_mapper_rejects_payload_digest_substitution() -> None:
    mapping = _mapping()
    request = _request(mapping)
    valid = _result(mapping, request).outputs[0]
    forged = object.__new__(WorkflowInlinePayload)
    for name in (
        "role",
        "owner_identity",
        "payload_type_identity",
        "schema_identity",
        "codec_identity",
        "representation_identity",
        "media_type",
        "payload",
        "byte_length",
    ):
        object.__setattr__(forged, name, getattr(valid, name))
    object.__setattr__(forged, "payload_sha256", "0" * 64)

    with pytest.raises(ValueError, match="payload_sha256 differs"):
        _execute(mapping, request, _result(mapping, request, output=forged))


def test_mapper_rejects_an_unregistered_external_variable() -> None:
    mapping = _mapping()
    request = _request(mapping)
    result = _result(mapping, request)
    wrong_transition = _transition(
        ColoredPetriNetBindingVariableIdentity("unregistered")
    )

    with pytest.raises(ValueError, match="external variables differ"):
        _execute(
            mapping,
            request,
            result,
            transition=wrong_transition,
        )


def test_mapper_rejects_non_success_variants_without_owner_imports() -> None:
    mapping = _mapping()
    request = _request(mapping)
    rejected = WorkflowFiringRejected(
        request_identity=request.identity,
        occurrence_identity=request.context.occurrence_identity,
        attempt_identity=request.context.attempt_identity,
        firer_identity=request.firer_identity,
        reason_codes=("not_admitted",),
        evidence=(),
    )

    with pytest.raises(TypeError, match="WorkflowFiringSucceeded"):
        ExperimentalWorkflowAsciiOutputMapper().execute(
            mapping=mapping,
            transition=_transition(),
            expected_context=request.context,
            request=request,
            result=rejected,  # type: ignore[arg-type]
        )

    source = inspect.getsource(
        __import__(
            "projectkoios.workflow.actions.mapping",
            fromlist=["ExperimentalWorkflowAsciiOutputMapper"],
        )
    )
    assert "projectkoios.simulations" not in source


def test_mapper_is_non_subclassable() -> None:
    with pytest.raises(TypeError, match="not subclassable"):

        class _InvalidMapper(ExperimentalWorkflowAsciiOutputMapper):
            pass
