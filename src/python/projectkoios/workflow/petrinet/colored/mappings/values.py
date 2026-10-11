"""Content-identified owner mappings between bounded typed values."""

import json
from dataclasses import dataclass, field
from hashlib import sha256

_MAX_SIGNED_64 = 9_223_372_036_854_775_807


@dataclass(frozen=True, slots=True)
class WorkflowValueMappingDescriptor:
    """One exact bounded owner adapter mapping between typed representations."""

    owner_identity: str
    adapter_identity: str
    adapter_version_identity: str
    input_record_type_identity: str
    output_record_type_identity: str
    input_payload_schema_identity: str
    input_payload_codec_identity: str
    output_payload_schema_identity: str
    output_payload_codec_identity: str
    correlation_descriptor_identities: tuple[str, ...]
    maximum_input_bytes: int
    maximum_output_bytes: int
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "owner_identity",
            "adapter_identity",
            "adapter_version_identity",
            "input_record_type_identity",
            "output_record_type_identity",
            "input_payload_schema_identity",
            "input_payload_codec_identity",
            "output_payload_schema_identity",
            "output_payload_codec_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        correlations = self.correlation_descriptor_identities
        if type(correlations) is not tuple or any(
            type(item) is not str or not item for item in correlations
        ):
            raise TypeError(
                "correlation_descriptor_identities must contain nonempty strings"
            )
        if correlations != tuple(sorted(set(correlations))):
            raise ValueError(
                "correlation_descriptor_identities must be unique and lexical"
            )
        for name in (
            "maximum_input_bytes",
            "maximum_output_bytes",
            "contract_version",
        ):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= _MAX_SIGNED_64:
                raise ValueError(
                    f"{name} must be a positive signed 64-bit integer"
                )
        state = {
            "adapter_identity": self.adapter_identity,
            "adapter_version_identity": self.adapter_version_identity,
            "contract_version": str(self.contract_version),
            "correlation_descriptor_identities": list(correlations),
            "input_payload_codec_identity": self.input_payload_codec_identity,
            "input_payload_schema_identity": self.input_payload_schema_identity,
            "input_record_type_identity": self.input_record_type_identity,
            "maximum_input_bytes": str(self.maximum_input_bytes),
            "maximum_output_bytes": str(self.maximum_output_bytes),
            "output_payload_codec_identity": self.output_payload_codec_identity,
            "output_payload_schema_identity": self.output_payload_schema_identity,
            "output_record_type_identity": self.output_record_type_identity,
            "owner_identity": self.owner_identity,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        object.__setattr__(
            self,
            "identity",
            "projectkoios.workflow.value-mapping-descriptor:0.1:"
            + sha256(encoded).hexdigest(),
        )
