"""Private fail-closed validation for experimental action mapping."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from string import hexdigits

from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowFiringRequest,
    WorkflowFiringSucceeded,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.payloads import (
    WorkflowInlinePayload,
    WorkflowPayloadContract,
)
from projectkoios.workflow_sdk.serialization import (
    WorkflowFirerDescriptorJsonCodec,
    WorkflowTransitionFirerBindingJsonCodec,
)

_MAX_IDENTITY_BYTES = 512


def _round_trip_transition_binding(
    value: WorkflowTransitionFirerBinding,
) -> WorkflowTransitionFirerBinding:
    codec = WorkflowTransitionFirerBindingJsonCodec()
    return codec.decode(codec.encode(value))


def _round_trip_firer_descriptor(
    value: WorkflowFirerDescriptor,
) -> WorkflowFirerDescriptor:
    codec = WorkflowFirerDescriptorJsonCodec()
    return codec.decode(codec.encode(value))


def _validate_payloads(
    values: tuple[WorkflowInlinePayload, ...],
    contracts: tuple[WorkflowPayloadContract, ...],
    label: str,
) -> None:
    if type(values) is not tuple:
        raise TypeError(f"{label} must be a tuple")
    if len(values) != len(contracts):
        raise ValueError(f"{label} must exactly satisfy retained contracts")
    for index, (value, contract) in enumerate(
        zip(values, contracts, strict=True)
    ):
        if type(value) is not WorkflowInlinePayload:
            raise TypeError(f"{label}[{index}] must be WorkflowInlinePayload")
        reconstructed = WorkflowInlinePayload(
            role=value.role,
            owner_identity=value.owner_identity,
            payload_type_identity=value.payload_type_identity,
            schema_identity=value.schema_identity,
            codec_identity=value.codec_identity,
            representation_identity=value.representation_identity,
            media_type=value.media_type,
            payload=value.payload,
            byte_length=value.byte_length,
            payload_sha256=value.payload_sha256,
        )
        if reconstructed != value:
            raise ValueError(f"{label}[{index}] differs after validation")
        metadata = (
            value.role,
            value.owner_identity,
            value.payload_type_identity,
            value.schema_identity,
            value.codec_identity,
            value.representation_identity,
            value.media_type,
        )
        expected = (
            contract.role,
            contract.owner_identity,
            contract.payload_type_identity,
            contract.schema_identity,
            contract.codec_identity,
            contract.representation_identity,
            contract.media_type,
        )
        if metadata != expected:
            raise ValueError(f"{label}[{index}] metadata differs from contract")
        if value.byte_length > contract.maximum_byte_length:
            raise ValueError(f"{label}[{index}] exceeds contract byte bound")


def _validate_bounds(
    descriptor: WorkflowFirerDescriptor,
    request: WorkflowFiringRequest,
    result: WorkflowFiringSucceeded,
) -> None:
    bounds = descriptor.bounds
    input_bytes = sum(item.byte_length for item in request.inputs)
    output_bytes = sum(item.byte_length for item in result.outputs)
    evidence_bytes = sum(item.byte_length for item in result.evidence)
    if len(request.inputs) > bounds.maximum_input_count:
        raise ValueError("request input count exceeds descriptor bounds")
    if len(result.outputs) > bounds.maximum_output_count:
        raise ValueError("result output count exceeds descriptor bounds")
    if len(result.evidence) > bounds.maximum_evidence_count:
        raise ValueError("result evidence count exceeds descriptor bounds")
    if input_bytes > bounds.maximum_input_bytes:
        raise ValueError("request input bytes exceed descriptor bounds")
    if output_bytes > bounds.maximum_output_bytes:
        raise ValueError("result output bytes exceed descriptor bounds")
    if (
        max(input_bytes, output_bytes + evidence_bytes)
        > bounds.maximum_total_bytes
    ):
        raise ValueError(
            "request or result bytes exceed descriptor total bound"
        )


def _decode_path_free_ascii_identity(payload: bytes, maximum: int) -> str:
    if type(payload) is not bytes:
        raise TypeError("identity payload must be built-in bytes")
    if (
        not payload
        or len(payload) > maximum
        or len(payload) > _MAX_IDENTITY_BYTES
    ):
        raise ValueError("identity payload exceeds its bounded ASCII contract")
    try:
        value = payload.decode("ascii")
    except UnicodeDecodeError as error:
        raise ValueError("identity payload must contain ASCII only") from error
    if any(byte <= 0x20 or byte == 0x7F for byte in payload):
        raise ValueError(
            "identity payload must not contain whitespace or controls"
        )
    lowered = value.lower()
    if (
        "/" in value
        or "\\" in value
        or value in {".", ".."}
        or value.startswith(("~", "./", "../"))
        or lowered.startswith("file:")
        or (
            len(value) >= 2
            and value[0].isascii()
            and value[0].isalpha()
            and value[1] == ":"
        )
    ):
        raise ValueError(
            "identity payload must not be a machine path or locator"
        )
    if value.encode("ascii") != payload:
        raise ValueError("identity payload is not exact canonical ASCII")
    return value


def _semantic_sha256(state: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            state,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _validate_ascii_token(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty and stripped")
    try:
        payload = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError(f"{label} must contain ASCII only") from error
    if any(byte <= 0x20 or byte == 0x7F for byte in payload):
        raise ValueError(f"{label} must not contain whitespace or controls")
