"""Experimental semantic mapping from retained sources to SDK inputs."""

from __future__ import annotations

from dataclasses import dataclass, field

from ._validation import (
    _semantic_sha256,
    _validate_ascii_token,
    _validate_sha256,
)

_INPUT_MAPPING_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-input-mapping:1"
)
_MAX_TOKEN_BYTES = 512


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowInputSourceProfileIdentity:
    """Nominal identity of one retained-input source representation profile."""

    value: str

    def __post_init__(self) -> None:
        _validate_bounded_token(
            self.value,
            "input source profile identity",
        )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputMappingDescriptorIdentity:
    """Content identity of one experimental input-source mapping."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "input mapping descriptor identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputMappingDescriptor:
    """Select one opaque retained-source profile for one SDK input role."""

    identity: ExperimentalWorkflowPureActionInputMappingDescriptorIdentity = (
        field(init=False)
    )
    input_role: str
    source_kind: str
    source_profile_identity: ExperimentalWorkflowInputSourceProfileIdentity
    mapping_version: str

    def __post_init__(self) -> None:
        _validate_bounded_token(self.input_role, "input role")
        _validate_bounded_token(self.source_kind, "source kind")
        if type(self.source_profile_identity) is not (
            ExperimentalWorkflowInputSourceProfileIdentity
        ):
            raise TypeError(
                "source_profile_identity must be "
                "ExperimentalWorkflowInputSourceProfileIdentity"
            )
        source_profile = ExperimentalWorkflowInputSourceProfileIdentity(
            self.source_profile_identity.value
        )
        if source_profile != self.source_profile_identity:
            raise ValueError("source profile differs after validation")
        _validate_bounded_token(self.mapping_version, "mapping version")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInputMappingDescriptorIdentity(
                _semantic_sha256(
                    {
                        "domain": _INPUT_MAPPING_DOMAIN,
                        "input_role": self.input_role,
                        "mapping_version": self.mapping_version,
                        "source_kind": self.source_kind,
                        "source_profile_identity": (source_profile.value),
                    }
                )
            ),
        )


def _validate_bounded_token(value: str, label: str) -> None:
    _validate_ascii_token(value, label)
    if len(value.encode("ascii")) > _MAX_TOKEN_BYTES:
        raise ValueError(f"{label} exceeds {_MAX_TOKEN_BYTES} bytes")


def _reconstruct_input_mapping(
    value: ExperimentalWorkflowPureActionInputMappingDescriptor,
) -> ExperimentalWorkflowPureActionInputMappingDescriptor:
    if type(value) is not ExperimentalWorkflowPureActionInputMappingDescriptor:
        raise TypeError(
            "input mapping must be "
            "ExperimentalWorkflowPureActionInputMappingDescriptor"
        )
    reconstructed = ExperimentalWorkflowPureActionInputMappingDescriptor(
        input_role=value.input_role,
        source_kind=value.source_kind,
        source_profile_identity=value.source_profile_identity,
        mapping_version=value.mapping_version,
    )
    if reconstructed != value:
        raise ValueError("input mapping differs after validation")
    return reconstructed


__all__ = [
    "ExperimentalWorkflowInputSourceProfileIdentity",
    "ExperimentalWorkflowPureActionInputMappingDescriptor",
    "ExperimentalWorkflowPureActionInputMappingDescriptorIdentity",
]
