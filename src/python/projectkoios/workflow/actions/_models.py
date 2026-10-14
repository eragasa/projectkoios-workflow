"""Immutable records for the experimental ASCII output mapping."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
)
from projectkoios.workflow_sdk.payloads import (
    WorkflowInlinePayload,
    WorkflowPayloadContract,
)
from projectkoios.workflow_sdk.serialization import (
    WorkflowFirerDescriptorJsonCodec,
    WorkflowTransitionFirerBindingJsonCodec,
)

from ._validation import (
    _decode_path_free_ascii_identity,
    _round_trip_firer_descriptor,
    _round_trip_transition_binding,
    _semantic_sha256,
    _validate_ascii_token,
    _validate_payloads,
    _validate_sha256,
)

_MAPPING_CONTRACT = "projectkoios.workflow.experimental-ascii-output-mapping:1"
_ASCII_DECODER_PROFILE = (
    "projectkoios.workflow.canonical-ascii-owner-logical-identity:1"
)
_ASCII_REPRESENTATION = "canonical-ascii:1"
_MAX_IDENTITY_BYTES = 512
_MAX_VERSION_BYTES = 128


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowActionResultMappingIdentity:
    """Content identity of one experimental owner-result mapping descriptor."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "mapping identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowMappedActionResultIdentity:
    """Content identity of one experimental mapped action result."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "mapped result identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowAsciiOutputMappingDescriptor:
    """Bind one exact SDK ASCII output to one shadow CPN string variable.

    The descriptor is immutable and content-identified. It embeds exact SDK
    transition and firer descriptors rather than owner implementations or
    codecs. The standalone SDK remains independent of the CPN implementation.
    """

    identity: ExperimentalWorkflowActionResultMappingIdentity = field(
        init=False
    )
    transition_binding: WorkflowTransitionFirerBinding
    firer_descriptor: WorkflowFirerDescriptor
    output_role: str
    external_variable_identity: ColoredPetriNetBindingVariableIdentity
    external_value_kind: ColoredPetriNetValueKind
    mapping_version: str
    decoder_profile_identity: str = _ASCII_DECODER_PROFILE

    def __post_init__(self) -> None:
        if type(self.transition_binding) is not WorkflowTransitionFirerBinding:
            raise TypeError(
                "transition_binding must be WorkflowTransitionFirerBinding"
            )
        if type(self.firer_descriptor) is not WorkflowFirerDescriptor:
            raise TypeError("firer_descriptor must be WorkflowFirerDescriptor")
        if type(self.external_variable_identity) is not (
            ColoredPetriNetBindingVariableIdentity
        ):
            raise TypeError(
                "external_variable_identity must be "
                "ColoredPetriNetBindingVariableIdentity"
            )
        if type(self.external_value_kind) is not ColoredPetriNetValueKind:
            raise TypeError(
                "external_value_kind must be ColoredPetriNetValueKind"
            )
        if self.external_value_kind is not ColoredPetriNetValueKind.STRING:
            raise ValueError(
                "experimental ASCII output mapping requires STRING"
            )
        _validate_ascii_token(self.mapping_version, "mapping_version")
        if len(self.mapping_version.encode("ascii")) > _MAX_VERSION_BYTES:
            raise ValueError("mapping_version exceeds 128 ASCII bytes")
        if type(self.decoder_profile_identity) is not str:
            raise TypeError("decoder_profile_identity must be a string")
        if self.decoder_profile_identity != _ASCII_DECODER_PROFILE:
            raise ValueError("unsupported ASCII decoder profile")

        binding = _round_trip_transition_binding(self.transition_binding)
        descriptor = _round_trip_firer_descriptor(self.firer_descriptor)
        if binding != self.transition_binding:
            raise ValueError(
                "transition binding differs after canonical round trip"
            )
        if descriptor != self.firer_descriptor:
            raise ValueError(
                "firer descriptor differs after canonical round trip"
            )
        if binding.firer_identity != descriptor.identity:
            raise ValueError("transition binding firer differs from descriptor")
        input_roles = tuple(
            contract.role for contract in descriptor.input_contracts
        )
        output_roles = tuple(
            contract.role for contract in descriptor.output_contracts
        )
        if binding.input_roles != input_roles:
            raise ValueError(
                "transition binding input roles differ from descriptor"
            )
        if binding.output_roles != output_roles:
            raise ValueError(
                "transition binding output roles differ from descriptor"
            )
        if len(descriptor.output_contracts) != 1:
            raise ValueError(
                "experimental ASCII mapping requires exactly one output"
            )
        if type(self.output_role) is not str:
            raise TypeError("output_role must be a string")
        if self.output_role != descriptor.output_contracts[0].role:
            raise ValueError(
                "output_role differs from the sole output contract"
            )
        output_contract = descriptor.output_contracts[0]
        if (
            output_contract.representation_identity.value
            != _ASCII_REPRESENTATION
        ):
            raise ValueError("output contract is not canonical ASCII")
        if output_contract.maximum_byte_length > _MAX_IDENTITY_BYTES:
            raise ValueError("ASCII logical identity bound exceeds 512 bytes")

        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowActionResultMappingIdentity(
                _mapping_descriptor_sha256(self)
            ),
        )

    @property
    def output_contract(self) -> WorkflowPayloadContract:
        """Return the sole exact canonical-ASCII output contract."""
        return self.firer_descriptor.output_contracts[0]

    @property
    def evidence_contracts(self) -> tuple[WorkflowPayloadContract, ...]:
        """Return the ordered evidence contracts retained by the mapper."""
        return self.firer_descriptor.evidence_contracts


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowMappedActionResult:
    """Retain one pure mapping and its exact SDK output/evidence correlation."""

    identity: ExperimentalWorkflowMappedActionResultIdentity = field(init=False)
    mapping_descriptor: ExperimentalWorkflowAsciiOutputMappingDescriptor
    request_identity: WorkflowFiringRequestIdentity
    result_identity: WorkflowFiringResultIdentity
    external_output_binding: ColoredPetriNetBinding
    source_output: WorkflowInlinePayload
    evidence: tuple[WorkflowInlinePayload, ...]

    def __post_init__(self) -> None:
        expected = (
            (
                "mapping_descriptor",
                self.mapping_descriptor,
                ExperimentalWorkflowAsciiOutputMappingDescriptor,
            ),
            (
                "request_identity",
                self.request_identity,
                WorkflowFiringRequestIdentity,
            ),
            (
                "result_identity",
                self.result_identity,
                WorkflowFiringResultIdentity,
            ),
            (
                "external_output_binding",
                self.external_output_binding,
                ColoredPetriNetBinding,
            ),
            ("source_output", self.source_output, WorkflowInlinePayload),
        )
        for name, value, nominal_type in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        mapping = self.mapping_descriptor
        validated_mapping = ExperimentalWorkflowAsciiOutputMappingDescriptor(
            transition_binding=mapping.transition_binding,
            firer_descriptor=mapping.firer_descriptor,
            output_role=mapping.output_role,
            external_variable_identity=mapping.external_variable_identity,
            external_value_kind=mapping.external_value_kind,
            mapping_version=mapping.mapping_version,
            decoder_profile_identity=mapping.decoder_profile_identity,
        )
        if validated_mapping != mapping:
            raise ValueError(
                "mapping descriptor differs from its content identity"
            )
        if type(self.evidence) is not tuple or any(
            type(item) is not WorkflowInlinePayload for item in self.evidence
        ):
            raise TypeError("evidence must be a tuple of WorkflowInlinePayload")
        _validate_payloads(
            (self.source_output,),
            (mapping.output_contract,),
            "mapped source output",
        )
        _validate_payloads(
            self.evidence,
            mapping.evidence_contracts,
            "mapped evidence",
        )
        binding = self.external_output_binding
        if binding.transition_identity.value != (
            mapping.transition_binding.transition_identity.value
        ):
            raise ValueError("mapped binding transition differs from mapping")
        if len(binding.assignments) != 1:
            raise ValueError(
                "mapped binding must contain exactly one assignment"
            )
        assignment = binding.assignments[0]
        if assignment.variable_identity != mapping.external_variable_identity:
            raise ValueError("mapped binding variable differs from mapping")
        if assignment.value.kind is not mapping.external_value_kind:
            raise ValueError("mapped binding value kind differs from mapping")
        identity_text = _decode_path_free_ascii_identity(
            self.source_output.payload,
            mapping.output_contract.maximum_byte_length,
        )
        if assignment.value.value != identity_text:
            raise ValueError("mapped binding value differs from owner output")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowMappedActionResultIdentity(
                _mapped_result_sha256(self)
            ),
        )

    @property
    def mapping_identity(
        self,
    ) -> ExperimentalWorkflowActionResultMappingIdentity:
        """Return the exact mapping-descriptor content identity."""
        return self.mapping_descriptor.identity


def _mapping_descriptor_sha256(
    value: ExperimentalWorkflowAsciiOutputMappingDescriptor,
) -> str:
    descriptor_payload = WorkflowFirerDescriptorJsonCodec().encode(
        value.firer_descriptor
    )
    binding_payload = WorkflowTransitionFirerBindingJsonCodec().encode(
        value.transition_binding
    )
    state = {
        "contract": _MAPPING_CONTRACT,
        "decoder_profile_identity": value.decoder_profile_identity,
        "external_value_kind": value.external_value_kind.value,
        "external_variable_identity": value.external_variable_identity.value,
        "firer_descriptor_sha256": hashlib.sha256(
            descriptor_payload
        ).hexdigest(),
        "mapping_version": value.mapping_version,
        "output_role": value.output_role,
        "transition_binding_sha256": hashlib.sha256(
            binding_payload
        ).hexdigest(),
    }
    return _semantic_sha256(state)


def _mapped_result_sha256(value: ExperimentalWorkflowMappedActionResult) -> str:
    assignments = [
        {
            "kind": assignment.value.kind.value,
            "value": assignment.value.value,
            "variable": assignment.variable_identity.value,
        }
        for assignment in value.external_output_binding.assignments
    ]
    transition_identity = (
        value.external_output_binding.transition_identity.value
    )
    state = {
        "contract": "projectkoios.workflow.experimental-mapped-action-result:1",
        "evidence": [
            {
                "byte_length": item.byte_length,
                "payload_sha256": item.payload_sha256,
                "role": item.role,
            }
            for item in value.evidence
        ],
        "external_output_binding": {
            "assignments": assignments,
            "transition_identity": transition_identity,
        },
        "mapping_identity": value.mapping_identity.value,
        "request_identity": value.request_identity.value,
        "result_identity": value.result_identity.value,
        "source_output": {
            "byte_length": value.source_output.byte_length,
            "payload_sha256": value.source_output.payload_sha256,
            "role": value.source_output.role,
        },
    }
    return _semantic_sha256(state)


__all__ = [
    "ExperimentalWorkflowActionResultMappingIdentity",
    "ExperimentalWorkflowAsciiOutputMappingDescriptor",
    "ExperimentalWorkflowMappedActionResult",
    "ExperimentalWorkflowMappedActionResultIdentity",
]
