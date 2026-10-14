"""Content-identified payload-reference bindings for CPN colors."""

import json
from dataclasses import dataclass, field
from hashlib import sha256

from ..definitions import CpnDefinitionIdentity
from ..values import CpnColorIdentity, CpnValueKind

_MAX_SIGNED_64 = 9_223_372_036_854_775_807


@dataclass(frozen=True, slots=True)
class WorkflowPayloadColorBinding:
    """Complete bounded payload-reference policy for one exact CPN color."""

    definition_identity: CpnDefinitionIdentity
    color_identity: CpnColorIdentity
    allowed_value_kind: CpnValueKind
    owner_identity: str
    payload_schema_identity: str
    codec_identity: str
    media_type_identity: str
    maximum_payload_bytes: int
    maximum_reference_tokens_per_complete_marking: int
    individual_token_identity_required: bool
    contract_version: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.definition_identity) is not CpnDefinitionIdentity:
            raise TypeError("definition_identity must be CpnDefinitionIdentity")
        if type(self.color_identity) is not CpnColorIdentity:
            raise TypeError("color_identity must be CpnColorIdentity")
        if self.allowed_value_kind is not CpnValueKind.STRING:
            raise ValueError("payload-reference colors must admit only STRING")
        for name in (
            "owner_identity",
            "payload_schema_identity",
            "codec_identity",
            "media_type_identity",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value:
                raise TypeError(f"{name} must be a nonempty string")
        for name in (
            "maximum_payload_bytes",
            "maximum_reference_tokens_per_complete_marking",
            "contract_version",
        ):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= _MAX_SIGNED_64:
                raise ValueError(
                    f"{name} must be a positive signed 64-bit integer"
                )
        if type(self.individual_token_identity_required) is not bool:
            raise TypeError("individual_token_identity_required must be bool")
        state = {
            "allowed_value_kind": self.allowed_value_kind.value,
            "codec_identity": self.codec_identity,
            "color_identity": self.color_identity.value,
            "contract_version": str(self.contract_version),
            "definition_identity": self.definition_identity.value,
            "individual_token_identity_required": (
                self.individual_token_identity_required
            ),
            "maximum_payload_bytes": str(self.maximum_payload_bytes),
            "maximum_reference_tokens_per_complete_marking": str(
                self.maximum_reference_tokens_per_complete_marking
            ),
            "media_type_identity": self.media_type_identity,
            "owner_identity": self.owner_identity,
            "payload_schema_identity": self.payload_schema_identity,
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
            "projectkoios.workflow.payload-color-binding:0.1:"
            + sha256(encoded).hexdigest(),
        )
