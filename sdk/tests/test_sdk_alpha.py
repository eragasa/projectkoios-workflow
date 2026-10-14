from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, replace
from typing import Any

import projectkoios.workflow_sdk as sdk_root
import projectkoios.workflow_sdk.firing as firing_module
import projectkoios.workflow_sdk.identities as identities_module
import projectkoios.workflow_sdk.integration as integration_module
import projectkoios.workflow_sdk.payloads as payloads_module
import projectkoios.workflow_sdk.serialization as serialization_module
import pytest
from projectkoios.workflow_sdk import WORKFLOW_SDK_VERSION
from projectkoios.workflow_sdk.firing import (
    Firer,
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowFiringFailed,
    WorkflowFiringRejected,
    WorkflowFiringRequest,
    WorkflowFiringResult,
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
    WorkflowIntegrationIdentity,
    WorkflowIntegrationManifestIdentity,
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
from projectkoios.workflow_sdk.integration import (
    WorkflowIntegrationManifest,
    WorkflowIntegrationManifestProvider,
    WorkflowWorkerIntegration,
)
from projectkoios.workflow_sdk.payloads import (
    WorkflowInlinePayload,
    WorkflowPayloadContract,
)
from projectkoios.workflow_sdk.serialization import (
    WorkflowFirerDescriptorJsonCodec,
    WorkflowFiringRequestJsonCodec,
    WorkflowFiringResultJsonCodec,
    WorkflowIntegrationManifestJsonCodec,
    WorkflowTransitionFirerBindingJsonCodec,
)


def test_public_symbol_inventory_is_exact() -> None:
    assert sdk_root.__all__ == [
        "WORKFLOW_SDK_CONTRACT_ID",
        "WORKFLOW_SDK_VERSION",
    ]
    assert set(identities_module.__all__) == {
        "WorkflowAttemptIdentity",
        "WorkflowDefinitionIdentity",
        "WorkflowFirerIdentity",
        "WorkflowFirerImplementationIdentity",
        "WorkflowFiringRequestIdentity",
        "WorkflowFiringResultIdentity",
        "WorkflowIntegrationIdentity",
        "WorkflowIntegrationManifestIdentity",
        "WorkflowMarkingIdentity",
        "WorkflowNetInstanceIdentity",
        "WorkflowOccurrenceIdentity",
        "WorkflowPayloadCodecIdentity",
        "WorkflowPayloadOwnerIdentity",
        "WorkflowPayloadRepresentationIdentity",
        "WorkflowPayloadSchemaIdentity",
        "WorkflowPayloadTypeIdentity",
        "WorkflowTransitionBindingIdentity",
        "WorkflowTransitionIdentity",
    }
    assert set(payloads_module.__all__) == {
        "WorkflowInlinePayload",
        "WorkflowPayloadContract",
    }
    assert set(firing_module.__all__) == {
        "Firer",
        "WorkflowFirerDescriptor",
        "WorkflowFiringBounds",
        "WorkflowFiringFailed",
        "WorkflowFiringRejected",
        "WorkflowFiringRequest",
        "WorkflowFiringResult",
        "WorkflowFiringSucceeded",
        "WorkflowOccurrenceContext",
        "WorkflowTransitionFirerBinding",
    }
    assert set(integration_module.__all__) == {
        "WorkflowIntegrationManifest",
        "WorkflowIntegrationManifestProvider",
        "WorkflowWorkerIntegration",
    }
    assert set(serialization_module.__all__) == {
        "WorkflowFirerDescriptorJsonCodec",
        "WorkflowFiringRequestJsonCodec",
        "WorkflowFiringResultJsonCodec",
        "WorkflowIntegrationManifestJsonCodec",
        "WorkflowTransitionFirerBindingJsonCodec",
    }


def _contract(role: str) -> WorkflowPayloadContract:
    return WorkflowPayloadContract(
        role=role,
        owner_identity=WorkflowPayloadOwnerIdentity("simulations"),
        payload_type_identity=WorkflowPayloadTypeIdentity(f"payload:{role}"),
        schema_identity=WorkflowPayloadSchemaIdentity(f"schema:{role}:1"),
        codec_identity=WorkflowPayloadCodecIdentity(f"codec:{role}:1"),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            "representation:canonical-json:1"
        ),
        media_type="application/json",
        maximum_byte_length=256,
    )


def _payload(contract: WorkflowPayloadContract, value: bytes) -> WorkflowInlinePayload:
    return WorkflowInlinePayload(
        role=contract.role,
        owner_identity=contract.owner_identity,
        payload_type_identity=contract.payload_type_identity,
        schema_identity=contract.schema_identity,
        codec_identity=contract.codec_identity,
        representation_identity=contract.representation_identity,
        media_type=contract.media_type,
        payload=value,
        byte_length=len(value),
        payload_sha256=hashlib.sha256(value).hexdigest(),
    )


def _descriptor() -> WorkflowFirerDescriptor:
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity("simulations.qe-artifact-set.project"),
        implementation_identity=WorkflowFirerImplementationIdentity(
            "simulations.qe-artifact-set.project:1"
        ),
        input_contracts=(_contract("request"),),
        output_contracts=(_contract("result"),),
        evidence_contracts=(_contract("evidence"),),
        bounds=WorkflowFiringBounds(
            maximum_input_count=1,
            maximum_output_count=1,
            maximum_evidence_count=1,
            maximum_input_bytes=256,
            maximum_output_bytes=256,
            maximum_total_bytes=512,
            maximum_reason_count=4,
        ),
    )


def _context() -> WorkflowOccurrenceContext:
    return WorkflowOccurrenceContext(
        definition_identity=WorkflowDefinitionIdentity("definition:1"),
        net_instance_identity=WorkflowNetInstanceIdentity("net:1"),
        transition_identity=WorkflowTransitionIdentity("transition:project"),
        predecessor_marking_identity=WorkflowMarkingIdentity("marking:1"),
        predecessor_revision=3,
        selected_binding_sha256="a" * 64,
        occurrence_identity=WorkflowOccurrenceIdentity("occurrence:1"),
        attempt_identity=WorkflowAttemptIdentity("attempt:1"),
        attempt_ordinal=0,
    )


def _binding(descriptor: WorkflowFirerDescriptor) -> WorkflowTransitionFirerBinding:
    return WorkflowTransitionFirerBinding(
        definition_identity=WorkflowDefinitionIdentity("definition:1"),
        transition_identity=WorkflowTransitionIdentity("transition:project"),
        firer_identity=descriptor.identity,
        input_roles=("request",),
        output_roles=("result",),
        binding_version="1",
    )


def _request(
    descriptor: WorkflowFirerDescriptor,
    binding: WorkflowTransitionFirerBinding,
) -> WorkflowFiringRequest:
    return WorkflowFiringRequest(
        context=_context(),
        binding_identity=binding.identity,
        firer_identity=descriptor.identity,
        inputs=(_payload(descriptor.input_contracts[0], b'{"request":1}'),),
    )


class _SuccessfulFirer(Firer):
    def __init__(self, descriptor: WorkflowFirerDescriptor) -> None:
        self._descriptor = descriptor

    @property
    def descriptor(self) -> WorkflowFirerDescriptor:
        return self._descriptor

    def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
        return WorkflowFiringSucceeded(
            request_identity=request.identity,
            occurrence_identity=request.context.occurrence_identity,
            attempt_identity=request.context.attempt_identity,
            firer_identity=request.firer_identity,
            outputs=(_payload(self.descriptor.output_contracts[0], b'{"result":1}'),),
            evidence=(_payload(self.descriptor.evidence_contracts[0], b'{"audit":1}'),),
        )


def test_firer_validates_and_returns_one_correlated_success() -> None:
    descriptor = _descriptor()
    binding = _binding(descriptor)
    request = _request(descriptor, binding)

    result = _SuccessfulFirer(descriptor).fire(request=request)

    assert type(result) is WorkflowFiringSucceeded
    assert result.request_identity == request.identity
    assert result.occurrence_identity == request.context.occurrence_identity
    assert result.attempt_identity == request.context.attempt_identity
    assert result.firer_identity == descriptor.identity
    assert result.outputs[0].role == "result"


def test_firer_template_method_is_runtime_non_overridable() -> None:
    with pytest.raises(TypeError, match="non-overridable"):

        class _InvalidFirer(Firer):
            @property
            def descriptor(self) -> WorkflowFirerDescriptor:
                return _descriptor()

            def fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
                return WorkflowFiringRejected(
                    request_identity=request.identity,
                    occurrence_identity=request.context.occurrence_identity,
                    attempt_identity=request.context.attempt_identity,
                    firer_identity=request.firer_identity,
                    reason_codes=("invalid",),
                    evidence=(),
                )

            def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
                raise AssertionError


def test_public_extension_points_are_nominal_abstract_bases() -> None:
    assert inspect.isabstract(Firer)
    assert inspect.isabstract(WorkflowFiringResult)
    assert inspect.isabstract(WorkflowIntegrationManifestProvider)
    assert inspect.isabstract(WorkflowWorkerIntegration)


def test_firer_rejects_unknown_result_class_and_wrong_correlation() -> None:
    descriptor = _descriptor()
    request = _request(descriptor, _binding(descriptor))

    class _UnknownResult(WorkflowFiringResult):
        @classmethod
        def _outcome(cls) -> str:
            return "unknown"

    class _UnknownResultFirer(Firer):
        @property
        def descriptor(self) -> WorkflowFirerDescriptor:
            return descriptor

        def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
            return _UnknownResult()

    with pytest.raises(TypeError, match="unsupported result type"):
        _UnknownResultFirer().fire(request=request)

    class _WrongCorrelationFirer(Firer):
        @property
        def descriptor(self) -> WorkflowFirerDescriptor:
            return descriptor

        def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
            return WorkflowFiringRejected(
                request_identity=WorkflowFiringRequestIdentity("0" * 64),
                occurrence_identity=request.context.occurrence_identity,
                attempt_identity=request.context.attempt_identity,
                firer_identity=request.firer_identity,
                reason_codes=("rejected",),
                evidence=(),
            )

    with pytest.raises(ValueError, match="correlation differs"):
        _WrongCorrelationFirer().fire(request=request)


def test_records_are_immutable_nominal_and_content_identified() -> None:
    descriptor = _descriptor()
    binding = _binding(descriptor)
    request = _request(descriptor, binding)

    with pytest.raises(FrozenInstanceError):
        request.firer_identity = WorkflowFirerIdentity("changed")  # type: ignore[misc]

    other_identity: object = WorkflowTransitionIdentity("same")
    assert WorkflowFirerIdentity("same") != other_identity
    assert binding == _binding(descriptor)
    assert request == _request(descriptor, binding)


def test_payload_rejects_wrong_digest_and_machine_path_identity() -> None:
    contract = _contract("request")
    with pytest.raises(ValueError, match="differs from payload"):
        replace(_payload(contract, b"value"), payload_sha256="0" * 64)
    with pytest.raises(ValueError, match="machine path"):
        WorkflowPayloadOwnerIdentity("/tmp/owner")


def test_all_canonical_codecs_round_trip() -> None:
    descriptor = _descriptor()
    binding = _binding(descriptor)
    request = _request(descriptor, binding)
    success = _SuccessfulFirer(descriptor).fire(request=request)
    rejected = WorkflowFiringRejected(
        request_identity=request.identity,
        occurrence_identity=request.context.occurrence_identity,
        attempt_identity=request.context.attempt_identity,
        firer_identity=request.firer_identity,
        reason_codes=("invalid_input",),
        evidence=(),
    )
    failed = WorkflowFiringFailed(
        request_identity=request.identity,
        occurrence_identity=request.context.occurrence_identity,
        attempt_identity=request.context.attempt_identity,
        firer_identity=request.firer_identity,
        failure_codes=("pure_failure",),
        evidence=(),
    )
    manifest = WorkflowIntegrationManifest(
        integration_identity=WorkflowIntegrationIdentity("simulations.qe"),
        package_name="projectkoios-simulations",
        package_version="0.1.0.dev0",
        distribution_sha256="b" * 64,
        sdk_contract_version=WORKFLOW_SDK_VERSION,
        firer_descriptors=(descriptor,),
    )

    values_and_codecs = (
        (descriptor, WorkflowFirerDescriptorJsonCodec()),
        (binding, WorkflowTransitionFirerBindingJsonCodec()),
        (request, WorkflowFiringRequestJsonCodec()),
        (success, WorkflowFiringResultJsonCodec()),
        (rejected, WorkflowFiringResultJsonCodec()),
        (failed, WorkflowFiringResultJsonCodec()),
        (manifest, WorkflowIntegrationManifestJsonCodec()),
    )
    for value, codec in values_and_codecs:
        payload = _round_trip(value, codec)
        assert payload == json.dumps(
            json.loads(payload),
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")


def _round_trip(value: Any, codec: Any) -> bytes:
    payload: bytes = codec.encode(value)
    assert codec.decode(payload) == value
    return payload


def test_decoder_rejects_noncanonical_duplicate_unknown_and_changed_identity() -> None:
    descriptor = _descriptor()
    codec = WorkflowFiringRequestJsonCodec()
    request = _request(descriptor, _binding(descriptor))
    payload = codec.encode(request)

    with pytest.raises(ValueError, match="exact canonical encoding"):
        codec.decode(payload + b" ")

    duplicate = payload.replace(b'{"request":', b'{"request":null,"request":', 1)
    with pytest.raises(ValueError, match="duplicate JSON key: request"):
        codec.decode(duplicate)

    document = json.loads(payload)
    document["unknown"] = True
    unknown = json.dumps(
        document, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode()
    with pytest.raises(ValueError, match="keys differ"):
        codec.decode(unknown)

    document.pop("unknown")
    document["request"]["identity"] = "0" * 64
    changed = json.dumps(
        document, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode()
    with pytest.raises(ValueError, match="identity differs"):
        codec.decode(changed)


def test_decoder_rejects_empty_oversized_and_overlong_collections() -> None:
    descriptor = _descriptor()
    codec = WorkflowFiringRequestJsonCodec()
    request = _request(descriptor, _binding(descriptor))

    with pytest.raises(ValueError, match="must contain"):
        codec.decode(b"")
    with pytest.raises(ValueError, match="must contain"):
        codec.decode(b"x" * (32 * 1024 * 1024 + 1))

    document = json.loads(codec.encode(request))
    document["request"]["inputs"] *= 65
    overlong = json.dumps(
        document, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode()
    with pytest.raises(ValueError, match="inputs exceeds 64 entries"):
        codec.decode(overlong)


def test_decoder_rejects_noncanonical_base64() -> None:
    descriptor = _descriptor()
    codec = WorkflowFiringRequestJsonCodec()
    payload = codec.encode(_request(descriptor, _binding(descriptor)))
    document = json.loads(payload)
    document["request"]["inputs"][0]["payload_base64"] = "e30"
    malformed = json.dumps(
        document, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode()

    with pytest.raises(ValueError, match="strict Base64|noncanonical"):
        codec.decode(malformed)


def test_codecs_are_not_subclassable() -> None:
    with pytest.raises(TypeError, match="not subclassable"):

        class _Codec(WorkflowFiringRequestJsonCodec):
            pass


def test_manifest_abcs_are_runtime_enforced() -> None:
    with pytest.raises(TypeError):
        WorkflowIntegrationManifestProvider()  # type: ignore[abstract]
    with pytest.raises(TypeError):
        WorkflowWorkerIntegration()  # type: ignore[abstract]

    class _Provider(WorkflowIntegrationManifestProvider):
        def manifest(self) -> WorkflowIntegrationManifest:
            return WorkflowIntegrationManifest(
                integration_identity=WorkflowIntegrationIdentity("integration"),
                package_name="package",
                package_version="1",
                distribution_sha256="c" * 64,
                sdk_contract_version=WORKFLOW_SDK_VERSION,
                firer_descriptors=(),
            )

    class _Worker(WorkflowWorkerIntegration):
        @property
        def manifest_identity(self) -> WorkflowIntegrationManifestIdentity:
            return _Provider().manifest().identity

        def firers(self) -> tuple[Firer, ...]:
            return ()

    assert type(_Provider().manifest()) is WorkflowIntegrationManifest
    assert _Worker().firers() == ()
