"""Strict canonical JSON codecs for Workflow SDK alpha records."""

from __future__ import annotations

import base64
import binascii
import json
from typing import NoReturn

from . import WORKFLOW_SDK_VERSION
from ._validation import (
    MAX_CONTRACTS,
    MAX_DOCUMENT_BYTES,
    MAX_INLINE_PAYLOAD_BYTES,
    MAX_PAYLOAD_COUNT,
    MAX_REASON_COUNT,
    closed_keys,
    require_array,
    require_integer,
    require_mapping,
    require_string,
    validate_depth,
)
from .firing import (
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
from .identities import (
    WorkflowAttemptIdentity,
    WorkflowDefinitionIdentity,
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
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
    WorkflowTransitionBindingIdentity,
    WorkflowTransitionIdentity,
)
from .integration import WorkflowIntegrationManifest
from .payloads import WorkflowInlinePayload, WorkflowPayloadContract

_DESCRIPTOR_SCHEMA = "projectkoios.workflow-sdk.firer-descriptor:1"
_BINDING_SCHEMA = "projectkoios.workflow-sdk.transition-firer-binding:1"
_REQUEST_SCHEMA = "projectkoios.workflow-sdk.firing-request:1"
_RESULT_SCHEMA = "projectkoios.workflow-sdk.firing-result:1"
_MANIFEST_SCHEMA = "projectkoios.workflow-sdk.integration-manifest:1"
_MAX_BASE64_CHARACTERS = 4 * ((MAX_INLINE_PAYLOAD_BYTES + 2) // 3)


class WorkflowFirerDescriptorJsonCodec:
    """Encode and decode one exact firer descriptor document."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError("WorkflowFirerDescriptorJsonCodec is not subclassable")

    def encode(self, value: WorkflowFirerDescriptor) -> bytes:
        if type(value) is not WorkflowFirerDescriptor:
            raise TypeError("value must be WorkflowFirerDescriptor")
        return _dump(_document(_DESCRIPTOR_SCHEMA, "descriptor", _descriptor(value)))

    def decode(self, payload: bytes) -> WorkflowFirerDescriptor:
        root = _root(_load(payload), _DESCRIPTOR_SCHEMA, "descriptor")
        value = _decode_descriptor(_mapping_field(root, "descriptor"))
        _require_canonical(self.encode(value), payload)
        return value


class WorkflowTransitionFirerBindingJsonCodec:
    """Encode and decode one exact transition-to-firer binding document."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError("WorkflowTransitionFirerBindingJsonCodec is not subclassable")

    def encode(self, value: WorkflowTransitionFirerBinding) -> bytes:
        if type(value) is not WorkflowTransitionFirerBinding:
            raise TypeError("value must be WorkflowTransitionFirerBinding")
        return _dump(_document(_BINDING_SCHEMA, "binding", _binding(value)))

    def decode(self, payload: bytes) -> WorkflowTransitionFirerBinding:
        root = _root(_load(payload), _BINDING_SCHEMA, "binding")
        item = _mapping_field(root, "binding")
        closed_keys(
            item,
            {
                "binding_version",
                "definition_identity",
                "firer_identity",
                "identity",
                "input_roles",
                "output_roles",
                "transition_identity",
            },
            "binding",
        )
        value = WorkflowTransitionFirerBinding(
            definition_identity=WorkflowDefinitionIdentity(
                _string_field(item, "definition_identity")
            ),
            transition_identity=WorkflowTransitionIdentity(
                _string_field(item, "transition_identity")
            ),
            firer_identity=WorkflowFirerIdentity(_string_field(item, "firer_identity")),
            input_roles=_string_tuple(
                item["input_roles"], "input_roles", MAX_PAYLOAD_COUNT
            ),
            output_roles=_string_tuple(
                item["output_roles"], "output_roles", MAX_PAYLOAD_COUNT
            ),
            binding_version=_string_field(item, "binding_version"),
        )
        supplied = WorkflowTransitionBindingIdentity(_string_field(item, "identity"))
        if value.identity != supplied:
            raise ValueError("binding identity differs from semantic content")
        _require_canonical(self.encode(value), payload)
        return value


class WorkflowFiringRequestJsonCodec:
    """Encode and decode one exact pure firing request document."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError("WorkflowFiringRequestJsonCodec is not subclassable")

    def encode(self, value: WorkflowFiringRequest) -> bytes:
        if type(value) is not WorkflowFiringRequest:
            raise TypeError("value must be WorkflowFiringRequest")
        return _dump(_document(_REQUEST_SCHEMA, "request", _request(value)))

    def decode(self, payload: bytes) -> WorkflowFiringRequest:
        root = _root(_load(payload), _REQUEST_SCHEMA, "request")
        item = _mapping_field(root, "request")
        closed_keys(
            item,
            {
                "binding_identity",
                "context",
                "firer_identity",
                "identity",
                "inputs",
                "sdk_contract_version",
            },
            "request",
        )
        value = WorkflowFiringRequest(
            context=_decode_context(_mapping_field(item, "context")),
            binding_identity=WorkflowTransitionBindingIdentity(
                _string_field(item, "binding_identity")
            ),
            firer_identity=WorkflowFirerIdentity(_string_field(item, "firer_identity")),
            inputs=tuple(
                _decode_inline_payload(_require_item_mapping(raw, "inputs", index))
                for index, raw in enumerate(
                    _array_field(item, "inputs", MAX_PAYLOAD_COUNT)
                )
            ),
            sdk_contract_version=_string_field(item, "sdk_contract_version"),
        )
        supplied = WorkflowFiringRequestIdentity(_string_field(item, "identity"))
        if value.identity != supplied:
            raise ValueError("request identity differs from semantic content")
        _require_canonical(self.encode(value), payload)
        return value


class WorkflowFiringResultJsonCodec:
    """Encode and decode the closed pure firing-result variants."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError("WorkflowFiringResultJsonCodec is not subclassable")

    def encode(self, value: WorkflowFiringResult) -> bytes:
        if type(value) is WorkflowFiringSucceeded:
            outcome = "succeeded"
        elif type(value) is WorkflowFiringRejected:
            outcome = "rejected"
        elif type(value) is WorkflowFiringFailed:
            outcome = "failed"
        else:
            raise TypeError("value must be an exact Workflow firing result")
        document: dict[str, object] = {
            "outcome": outcome,
            "result": _result(value),
            "schema_identity": _RESULT_SCHEMA,
            "sdk_contract_version": WORKFLOW_SDK_VERSION,
        }
        return _dump(document)

    def decode(self, payload: bytes) -> WorkflowFiringResult:
        root = require_mapping(_load(payload), "document")
        closed_keys(
            root,
            {"outcome", "result", "schema_identity", "sdk_contract_version"},
            "document",
        )
        _require_root_metadata(root, _RESULT_SCHEMA)
        outcome = _string_field(root, "outcome")
        item = _mapping_field(root, "result")
        if outcome == "succeeded":
            value: WorkflowFiringResult = _decode_succeeded(item)
        elif outcome == "rejected":
            value = _decode_rejected(item)
        elif outcome == "failed":
            value = _decode_failed(item)
        else:
            raise ValueError("unsupported firing result outcome")
        _require_canonical(self.encode(value), payload)
        return value


class WorkflowIntegrationManifestJsonCodec:
    """Encode and decode one exact immutable integration manifest."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError("WorkflowIntegrationManifestJsonCodec is not subclassable")

    def encode(self, value: WorkflowIntegrationManifest) -> bytes:
        if type(value) is not WorkflowIntegrationManifest:
            raise TypeError("value must be WorkflowIntegrationManifest")
        return _dump(_document(_MANIFEST_SCHEMA, "manifest", _manifest(value)))

    def decode(self, payload: bytes) -> WorkflowIntegrationManifest:
        root = _root(_load(payload), _MANIFEST_SCHEMA, "manifest")
        item = _mapping_field(root, "manifest")
        closed_keys(
            item,
            {
                "distribution_sha256",
                "firer_descriptors",
                "identity",
                "integration_identity",
                "package_name",
                "package_version",
                "sdk_contract_version",
            },
            "manifest",
        )
        value = WorkflowIntegrationManifest(
            integration_identity=WorkflowIntegrationIdentity(
                _string_field(item, "integration_identity")
            ),
            package_name=_string_field(item, "package_name"),
            package_version=_string_field(item, "package_version"),
            distribution_sha256=_string_field(item, "distribution_sha256"),
            sdk_contract_version=_string_field(item, "sdk_contract_version"),
            firer_descriptors=tuple(
                _decode_descriptor(
                    _require_item_mapping(raw, "firer_descriptors", index)
                )
                for index, raw in enumerate(
                    _array_field(item, "firer_descriptors", MAX_CONTRACTS)
                )
            ),
        )
        supplied = WorkflowIntegrationManifestIdentity(_string_field(item, "identity"))
        if value.identity != supplied:
            raise ValueError("manifest identity differs from semantic content")
        _require_canonical(self.encode(value), payload)
        return value


def _document(schema: str, field: str, value: object) -> dict[str, object]:
    return {
        field: value,
        "schema_identity": schema,
        "sdk_contract_version": WORKFLOW_SDK_VERSION,
    }


def _root(value: object, schema: str, field: str) -> dict[str, object]:
    root = require_mapping(value, "document")
    closed_keys(
        root,
        {field, "schema_identity", "sdk_contract_version"},
        "document",
    )
    _require_root_metadata(root, schema)
    return root


def _require_root_metadata(root: dict[str, object], schema: str) -> None:
    if _string_field(root, "schema_identity") != schema:
        raise ValueError("unsupported schema identity")
    if _string_field(root, "sdk_contract_version") != WORKFLOW_SDK_VERSION:
        raise ValueError("unsupported SDK contract version")


def _descriptor(value: WorkflowFirerDescriptor) -> dict[str, object]:
    return {
        "bounds": _bounds(value.bounds),
        "evidence_contracts": [
            _payload_contract(item) for item in value.evidence_contracts
        ],
        "identity": value.identity.value,
        "implementation_identity": value.implementation_identity.value,
        "input_contracts": [_payload_contract(item) for item in value.input_contracts],
        "output_contracts": [
            _payload_contract(item) for item in value.output_contracts
        ],
        "sdk_contract_version": value.sdk_contract_version,
    }


def _decode_descriptor(item: dict[str, object]) -> WorkflowFirerDescriptor:
    closed_keys(
        item,
        {
            "bounds",
            "evidence_contracts",
            "identity",
            "implementation_identity",
            "input_contracts",
            "output_contracts",
            "sdk_contract_version",
        },
        "descriptor",
    )
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity(_string_field(item, "identity")),
        implementation_identity=WorkflowFirerImplementationIdentity(
            _string_field(item, "implementation_identity")
        ),
        input_contracts=_decode_contract_tuple(item, "input_contracts"),
        output_contracts=_decode_contract_tuple(item, "output_contracts"),
        evidence_contracts=_decode_contract_tuple(item, "evidence_contracts"),
        bounds=_decode_bounds(_mapping_field(item, "bounds")),
        sdk_contract_version=_string_field(item, "sdk_contract_version"),
    )


def _payload_contract(value: WorkflowPayloadContract) -> dict[str, object]:
    return {
        "codec_identity": value.codec_identity.value,
        "maximum_byte_length": value.maximum_byte_length,
        "media_type": value.media_type,
        "owner_identity": value.owner_identity.value,
        "payload_type_identity": value.payload_type_identity.value,
        "representation_identity": value.representation_identity.value,
        "role": value.role,
        "schema_identity": value.schema_identity.value,
    }


def _decode_payload_contract(item: dict[str, object]) -> WorkflowPayloadContract:
    closed_keys(
        item,
        {
            "codec_identity",
            "maximum_byte_length",
            "media_type",
            "owner_identity",
            "payload_type_identity",
            "representation_identity",
            "role",
            "schema_identity",
        },
        "payload contract",
    )
    return WorkflowPayloadContract(
        role=_string_field(item, "role"),
        owner_identity=WorkflowPayloadOwnerIdentity(
            _string_field(item, "owner_identity")
        ),
        payload_type_identity=WorkflowPayloadTypeIdentity(
            _string_field(item, "payload_type_identity")
        ),
        schema_identity=WorkflowPayloadSchemaIdentity(
            _string_field(item, "schema_identity")
        ),
        codec_identity=WorkflowPayloadCodecIdentity(
            _string_field(item, "codec_identity")
        ),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            _string_field(item, "representation_identity")
        ),
        media_type=_string_field(item, "media_type"),
        maximum_byte_length=_integer_field(item, "maximum_byte_length"),
    )


def _inline_payload(value: WorkflowInlinePayload) -> dict[str, object]:
    return {
        "byte_length": value.byte_length,
        "codec_identity": value.codec_identity.value,
        "media_type": value.media_type,
        "owner_identity": value.owner_identity.value,
        "payload_base64": base64.b64encode(value.payload).decode("ascii"),
        "payload_sha256": value.payload_sha256,
        "payload_type_identity": value.payload_type_identity.value,
        "representation_identity": value.representation_identity.value,
        "role": value.role,
        "schema_identity": value.schema_identity.value,
    }


def _decode_inline_payload(item: dict[str, object]) -> WorkflowInlinePayload:
    closed_keys(
        item,
        {
            "byte_length",
            "codec_identity",
            "media_type",
            "owner_identity",
            "payload_base64",
            "payload_sha256",
            "payload_type_identity",
            "representation_identity",
            "role",
            "schema_identity",
        },
        "inline payload",
    )
    encoded = _string_field(item, "payload_base64")
    if len(encoded) > _MAX_BASE64_CHARACTERS:
        raise ValueError("payload_base64 exceeds SDK bound")
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError("payload_base64 must be strict Base64") from error
    if base64.b64encode(payload).decode("ascii") != encoded:
        raise ValueError("payload_base64 is noncanonical")
    return WorkflowInlinePayload(
        role=_string_field(item, "role"),
        owner_identity=WorkflowPayloadOwnerIdentity(
            _string_field(item, "owner_identity")
        ),
        payload_type_identity=WorkflowPayloadTypeIdentity(
            _string_field(item, "payload_type_identity")
        ),
        schema_identity=WorkflowPayloadSchemaIdentity(
            _string_field(item, "schema_identity")
        ),
        codec_identity=WorkflowPayloadCodecIdentity(
            _string_field(item, "codec_identity")
        ),
        representation_identity=WorkflowPayloadRepresentationIdentity(
            _string_field(item, "representation_identity")
        ),
        media_type=_string_field(item, "media_type"),
        payload=payload,
        byte_length=_integer_field(item, "byte_length"),
        payload_sha256=_string_field(item, "payload_sha256"),
    )


def _bounds(value: WorkflowFiringBounds) -> dict[str, object]:
    return {
        "maximum_evidence_count": value.maximum_evidence_count,
        "maximum_input_bytes": value.maximum_input_bytes,
        "maximum_input_count": value.maximum_input_count,
        "maximum_output_bytes": value.maximum_output_bytes,
        "maximum_output_count": value.maximum_output_count,
        "maximum_reason_count": value.maximum_reason_count,
        "maximum_total_bytes": value.maximum_total_bytes,
    }


def _decode_bounds(item: dict[str, object]) -> WorkflowFiringBounds:
    expected = {
        "maximum_evidence_count",
        "maximum_input_bytes",
        "maximum_input_count",
        "maximum_output_bytes",
        "maximum_output_count",
        "maximum_reason_count",
        "maximum_total_bytes",
    }
    closed_keys(item, expected, "bounds")
    return WorkflowFiringBounds(
        maximum_input_count=_integer_field(item, "maximum_input_count"),
        maximum_output_count=_integer_field(item, "maximum_output_count"),
        maximum_evidence_count=_integer_field(item, "maximum_evidence_count"),
        maximum_input_bytes=_integer_field(item, "maximum_input_bytes"),
        maximum_output_bytes=_integer_field(item, "maximum_output_bytes"),
        maximum_total_bytes=_integer_field(item, "maximum_total_bytes"),
        maximum_reason_count=_integer_field(item, "maximum_reason_count"),
    )


def _context(value: WorkflowOccurrenceContext) -> dict[str, object]:
    return {
        "attempt_identity": value.attempt_identity.value,
        "attempt_ordinal": value.attempt_ordinal,
        "definition_identity": value.definition_identity.value,
        "net_instance_identity": value.net_instance_identity.value,
        "occurrence_identity": value.occurrence_identity.value,
        "predecessor_marking_identity": value.predecessor_marking_identity.value,
        "predecessor_revision": value.predecessor_revision,
        "selected_binding_sha256": value.selected_binding_sha256,
        "transition_identity": value.transition_identity.value,
    }


def _decode_context(item: dict[str, object]) -> WorkflowOccurrenceContext:
    closed_keys(
        item,
        {
            "attempt_identity",
            "attempt_ordinal",
            "definition_identity",
            "net_instance_identity",
            "occurrence_identity",
            "predecessor_marking_identity",
            "predecessor_revision",
            "selected_binding_sha256",
            "transition_identity",
        },
        "context",
    )
    return WorkflowOccurrenceContext(
        definition_identity=WorkflowDefinitionIdentity(
            _string_field(item, "definition_identity")
        ),
        net_instance_identity=WorkflowNetInstanceIdentity(
            _string_field(item, "net_instance_identity")
        ),
        transition_identity=WorkflowTransitionIdentity(
            _string_field(item, "transition_identity")
        ),
        predecessor_marking_identity=WorkflowMarkingIdentity(
            _string_field(item, "predecessor_marking_identity")
        ),
        predecessor_revision=_integer_field(item, "predecessor_revision"),
        selected_binding_sha256=_string_field(item, "selected_binding_sha256"),
        occurrence_identity=WorkflowOccurrenceIdentity(
            _string_field(item, "occurrence_identity")
        ),
        attempt_identity=WorkflowAttemptIdentity(
            _string_field(item, "attempt_identity")
        ),
        attempt_ordinal=_integer_field(item, "attempt_ordinal"),
    )


def _binding(value: WorkflowTransitionFirerBinding) -> dict[str, object]:
    return {
        "binding_version": value.binding_version,
        "definition_identity": value.definition_identity.value,
        "firer_identity": value.firer_identity.value,
        "identity": value.identity.value,
        "input_roles": list(value.input_roles),
        "output_roles": list(value.output_roles),
        "transition_identity": value.transition_identity.value,
    }


def _request(value: WorkflowFiringRequest) -> dict[str, object]:
    return {
        "binding_identity": value.binding_identity.value,
        "context": _context(value.context),
        "firer_identity": value.firer_identity.value,
        "identity": value.identity.value,
        "inputs": [_inline_payload(item) for item in value.inputs],
        "sdk_contract_version": value.sdk_contract_version,
    }


def _result(value: WorkflowFiringResult) -> dict[str, object]:
    assert type(value) in (
        WorkflowFiringSucceeded,
        WorkflowFiringRejected,
        WorkflowFiringFailed,
    )
    result: dict[str, object] = {
        "attempt_identity": value.attempt_identity.value,
        "evidence": [_inline_payload(item) for item in value.evidence],
        "firer_identity": value.firer_identity.value,
        "identity": value.identity.value,
        "occurrence_identity": value.occurrence_identity.value,
        "request_identity": value.request_identity.value,
        "sdk_contract_version": value.sdk_contract_version,
    }
    if type(value) is WorkflowFiringSucceeded:
        result["outputs"] = [_inline_payload(item) for item in value.outputs]
    elif type(value) is WorkflowFiringRejected:
        result["reason_codes"] = list(value.reason_codes)
    else:
        assert type(value) is WorkflowFiringFailed
        result["failure_codes"] = list(value.failure_codes)
    return result


def _decode_succeeded(item: dict[str, object]) -> WorkflowFiringSucceeded:
    _closed_result_keys(item, "outputs")
    value = WorkflowFiringSucceeded(
        request_identity=WorkflowFiringRequestIdentity(
            _string_field(item, "request_identity")
        ),
        occurrence_identity=WorkflowOccurrenceIdentity(
            _string_field(item, "occurrence_identity")
        ),
        attempt_identity=WorkflowAttemptIdentity(
            _string_field(item, "attempt_identity")
        ),
        firer_identity=WorkflowFirerIdentity(_string_field(item, "firer_identity")),
        outputs=_decode_payload_tuple(item, "outputs"),
        evidence=_decode_payload_tuple(item, "evidence"),
        sdk_contract_version=_string_field(item, "sdk_contract_version"),
    )
    _require_result_identity(value, item)
    return value


def _decode_rejected(item: dict[str, object]) -> WorkflowFiringRejected:
    _closed_result_keys(item, "reason_codes")
    value = WorkflowFiringRejected(
        request_identity=WorkflowFiringRequestIdentity(
            _string_field(item, "request_identity")
        ),
        occurrence_identity=WorkflowOccurrenceIdentity(
            _string_field(item, "occurrence_identity")
        ),
        attempt_identity=WorkflowAttemptIdentity(
            _string_field(item, "attempt_identity")
        ),
        firer_identity=WorkflowFirerIdentity(_string_field(item, "firer_identity")),
        reason_codes=_string_tuple(
            item["reason_codes"], "reason_codes", MAX_REASON_COUNT
        ),
        evidence=_decode_payload_tuple(item, "evidence"),
        sdk_contract_version=_string_field(item, "sdk_contract_version"),
    )
    _require_result_identity(value, item)
    return value


def _decode_failed(item: dict[str, object]) -> WorkflowFiringFailed:
    _closed_result_keys(item, "failure_codes")
    value = WorkflowFiringFailed(
        request_identity=WorkflowFiringRequestIdentity(
            _string_field(item, "request_identity")
        ),
        occurrence_identity=WorkflowOccurrenceIdentity(
            _string_field(item, "occurrence_identity")
        ),
        attempt_identity=WorkflowAttemptIdentity(
            _string_field(item, "attempt_identity")
        ),
        firer_identity=WorkflowFirerIdentity(_string_field(item, "firer_identity")),
        failure_codes=_string_tuple(
            item["failure_codes"], "failure_codes", MAX_REASON_COUNT
        ),
        evidence=_decode_payload_tuple(item, "evidence"),
        sdk_contract_version=_string_field(item, "sdk_contract_version"),
    )
    _require_result_identity(value, item)
    return value


def _closed_result_keys(item: dict[str, object], variant_field: str) -> None:
    closed_keys(
        item,
        {
            "attempt_identity",
            "evidence",
            "firer_identity",
            "identity",
            "occurrence_identity",
            "request_identity",
            "sdk_contract_version",
            variant_field,
        },
        "result",
    )


def _require_result_identity(
    value: WorkflowFiringResult, item: dict[str, object]
) -> None:
    supplied = WorkflowFiringResultIdentity(_string_field(item, "identity"))
    if value.identity != supplied:
        raise ValueError("result identity differs from semantic content")


def _manifest(value: WorkflowIntegrationManifest) -> dict[str, object]:
    return {
        "distribution_sha256": value.distribution_sha256,
        "firer_descriptors": [_descriptor(item) for item in value.firer_descriptors],
        "identity": value.identity.value,
        "integration_identity": value.integration_identity.value,
        "package_name": value.package_name,
        "package_version": value.package_version,
        "sdk_contract_version": value.sdk_contract_version,
    }


def _decode_contract_tuple(
    item: dict[str, object], field: str
) -> tuple[WorkflowPayloadContract, ...]:
    return tuple(
        _decode_payload_contract(_require_item_mapping(raw, field, index))
        for index, raw in enumerate(_array_field(item, field, MAX_CONTRACTS))
    )


def _decode_payload_tuple(
    item: dict[str, object], field: str
) -> tuple[WorkflowInlinePayload, ...]:
    return tuple(
        _decode_inline_payload(_require_item_mapping(raw, field, index))
        for index, raw in enumerate(_array_field(item, field, MAX_PAYLOAD_COUNT))
    )


def _mapping_field(item: dict[str, object], field: str) -> dict[str, object]:
    return require_mapping(item[field], field)


def _array_field(item: dict[str, object], field: str, maximum: int) -> list[object]:
    values = require_array(item[field], field)
    if len(values) > maximum:
        raise ValueError(f"{field} exceeds {maximum} entries")
    return values


def _string_field(item: dict[str, object], field: str) -> str:
    return require_string(item[field], field)


def _integer_field(item: dict[str, object], field: str) -> int:
    return require_integer(item[field], field)


def _string_tuple(value: object, label: str, maximum: int) -> tuple[str, ...]:
    values = require_array(value, label)
    if len(values) > maximum:
        raise ValueError(f"{label} exceeds {maximum} entries")
    return tuple(
        require_string(item, f"{label}[{index}]") for index, item in enumerate(values)
    )


def _require_item_mapping(value: object, label: str, index: int) -> dict[str, object]:
    return require_mapping(value, f"{label}[{index}]")


def _load(payload: bytes) -> object:
    if type(payload) is not bytes:
        raise TypeError("payload must be built-in bytes")
    if not payload or len(payload) > MAX_DOCUMENT_BYTES:
        raise ValueError(f"payload must contain 1..{MAX_DOCUMENT_BYTES} bytes")
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError("payload must not contain a UTF-8 BOM")
    try:
        text = payload.decode("utf-8", errors="strict")
        value: object = json.loads(
            text,
            object_pairs_hook=_object_pairs,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("payload must be one valid UTF-8 JSON object") from error
    validate_depth(value)
    return value


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_number(value: str) -> NoReturn:
    raise ValueError(f"unsupported JSON number: {value}")


def _dump(value: dict[str, object]) -> bytes:
    payload = json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if not payload or len(payload) > MAX_DOCUMENT_BYTES:
        raise ValueError("encoded document exceeds SDK bound")
    return payload


def _require_canonical(expected: bytes, supplied: bytes) -> None:
    if expected != supplied:
        raise ValueError("payload is not the exact canonical encoding")


__all__ = [
    "WorkflowFirerDescriptorJsonCodec",
    "WorkflowFiringRequestJsonCodec",
    "WorkflowFiringResultJsonCodec",
    "WorkflowIntegrationManifestJsonCodec",
    "WorkflowTransitionFirerBindingJsonCodec",
]
