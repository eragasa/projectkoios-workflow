"""Experimental source-correlated input admission for pure external actions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from string import hexdigits
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowFiringRequestCoordinates,
    ExperimentalWorkflowFiringRequestFactory,
    ExperimentalWorkflowInputSourceProfileIdentity,
    ExperimentalWorkflowSelectedBindingEvidence,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionInputBindings,
    ExperimentalWorkflowPureActionInputPlan,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow_sdk.firing import WorkflowFiringRequest
from projectkoios.workflow_sdk.payloads import WorkflowInlinePayload

_SOURCE_EVIDENCE_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-input-source-evidence:1"
)
_ADMITTED_INPUTS_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-admitted-inputs:1"
)
_MAX_SOURCE_IDENTITY_BYTES = 512


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceEvidenceIdentity:
    """Content identity of one exact opaque input-source evidence record."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "input source evidence identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionAdmittedInputsIdentity:
    """Content identity of one exact admitted SDK input tuple."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "admitted inputs identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceEvidence:
    """Bind exact SDK payload bytes to one opaque retained source."""

    identity: ExperimentalWorkflowPureActionInputSourceEvidenceIdentity = field(
        init=False
    )
    source_kind: str
    source_profile_identity: ExperimentalWorkflowInputSourceProfileIdentity
    source_identity: str
    payload: WorkflowInlinePayload

    def __post_init__(self) -> None:
        _validate_ascii_token(self.source_kind, "source kind")
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
        _validate_opaque_source_identity(self.source_identity)
        if type(self.payload) is not WorkflowInlinePayload:
            raise TypeError("payload must be WorkflowInlinePayload")
        payload = _reconstruct_payload(self.payload)
        if payload != self.payload:
            raise ValueError("source payload differs after validation")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInputSourceEvidenceIdentity(
                stable_identity(
                    _SOURCE_EVIDENCE_DOMAIN,
                    self.source_kind,
                    source_profile.value,
                    self.source_identity,
                    payload.role,
                    payload.owner_identity.value,
                    payload.payload_type_identity.value,
                    payload.schema_identity.value,
                    payload.codec_identity.value,
                    payload.representation_identity.value,
                    payload.media_type,
                    payload.byte_length,
                    payload.payload_sha256,
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionAdmittedInputs:
    """Close exact source evidence over one invocation candidate."""

    identity: ExperimentalWorkflowPureActionAdmittedInputsIdentity = field(
        init=False
    )
    input_bindings: ExperimentalWorkflowPureActionInputBindings
    selected_binding_evidence: ExperimentalWorkflowSelectedBindingEvidence
    coordinates: ExperimentalWorkflowFiringRequestCoordinates
    source_evidence: tuple[
        ExperimentalWorkflowPureActionInputSourceEvidence, ...
    ]
    request: WorkflowFiringRequest

    def __post_init__(self) -> None:
        bindings = _reconstruct_input_bindings(self.input_bindings)
        evidence = _reconstruct_selected_binding_evidence(
            self.selected_binding_evidence
        )
        coordinates = _reconstruct_coordinates(self.coordinates)
        if type(self.source_evidence) is not tuple:
            raise TypeError("source_evidence must be a tuple")
        sources = tuple(
            _reconstruct_source_evidence(value)
            for value in self.source_evidence
        )
        if sources != self.source_evidence:
            raise ValueError("source evidence differs after validation")
        mappings = bindings.input_plan.input_mappings
        if len(sources) != len(mappings):
            raise ValueError(
                "source evidence must exactly satisfy input mappings"
            )
        for index, (source, mapping) in enumerate(
            zip(sources, mappings, strict=True)
        ):
            if source.payload.role != mapping.input_role:
                raise ValueError(
                    f"source_evidence[{index}] role differs from mapping"
                )
            if source.source_kind != mapping.source_kind:
                raise ValueError(
                    f"source_evidence[{index}] kind differs from mapping"
                )
            if (
                source.source_profile_identity
                != mapping.source_profile_identity
            ):
                raise ValueError(
                    f"source_evidence[{index}] profile differs from mapping"
                )
        base_plan = bindings.input_plan.execution_plan
        if (
            evidence.profile_identity
            != base_plan.selected_binding_profile_identity
        ):
            raise ValueError("selected-binding profile differs from input plan")
        output_mapping = base_plan.output_mapping_descriptor
        request = ExperimentalWorkflowFiringRequestFactory().execute(
            transition_binding=output_mapping.transition_binding,
            firer_descriptor=output_mapping.firer_descriptor,
            selected_binding_evidence=evidence,
            coordinates=coordinates,
            inputs=tuple(value.payload for value in sources),
        )
        if type(self.request) is not WorkflowFiringRequest:
            raise TypeError("request must be WorkflowFiringRequest")
        if request != self.request:
            raise ValueError("request differs from admitted source evidence")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionAdmittedInputsIdentity(
                stable_identity(
                    _ADMITTED_INPUTS_DOMAIN,
                    bindings.identity.value,
                    evidence.identity.value,
                    request.identity.value,
                    tuple(value.identity.value for value in sources),
                )
            ),
        )


@final
class ExperimentalWorkflowPureActionInputAdmissionFactory:
    """Construct one structurally admitted input tuple from source evidence."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionInputAdmissionFactory "
            "is not subclassable"
        )

    def execute(
        self,
        *,
        input_bindings: ExperimentalWorkflowPureActionInputBindings,
        selected_binding_evidence: ExperimentalWorkflowSelectedBindingEvidence,
        coordinates: ExperimentalWorkflowFiringRequestCoordinates,
        source_evidence: tuple[
            ExperimentalWorkflowPureActionInputSourceEvidence, ...
        ],
    ) -> ExperimentalWorkflowPureActionAdmittedInputs:
        """Validate exact sources and construct the correlated SDK request."""
        bindings = _reconstruct_input_bindings(input_bindings)
        evidence = _reconstruct_selected_binding_evidence(
            selected_binding_evidence
        )
        invocation_coordinates = _reconstruct_coordinates(coordinates)
        if type(source_evidence) is not tuple:
            raise TypeError("source_evidence must be a tuple")
        sources = tuple(
            _reconstruct_source_evidence(value) for value in source_evidence
        )
        base_plan = bindings.input_plan.execution_plan
        if (
            evidence.profile_identity
            != base_plan.selected_binding_profile_identity
        ):
            raise ValueError("selected-binding profile differs from input plan")
        output_mapping = base_plan.output_mapping_descriptor
        request = ExperimentalWorkflowFiringRequestFactory().execute(
            transition_binding=output_mapping.transition_binding,
            firer_descriptor=output_mapping.firer_descriptor,
            selected_binding_evidence=evidence,
            coordinates=invocation_coordinates,
            inputs=tuple(value.payload for value in sources),
        )
        return ExperimentalWorkflowPureActionAdmittedInputs(
            input_bindings=bindings,
            selected_binding_evidence=evidence,
            coordinates=invocation_coordinates,
            source_evidence=sources,
            request=request,
        )


def _reconstruct_input_bindings(
    value: ExperimentalWorkflowPureActionInputBindings,
) -> ExperimentalWorkflowPureActionInputBindings:
    if type(value) is not ExperimentalWorkflowPureActionInputBindings:
        raise TypeError(
            "input_bindings must be ExperimentalWorkflowPureActionInputBindings"
        )
    reconstructed = ExperimentalWorkflowPureActionInputBindings(
        input_plan=ExperimentalWorkflowPureActionInputPlan(
            execution_plan=value.input_plan.execution_plan,
            input_mappings=value.input_plan.input_mappings,
        ),
        execution_bindings=ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=value.execution_bindings.execution_plan,
            integration_manifest=value.execution_bindings.integration_manifest,
        ),
    )
    if reconstructed != value:
        raise ValueError("input bindings differ after validation")
    return reconstructed


def _reconstruct_selected_binding_evidence(
    value: ExperimentalWorkflowSelectedBindingEvidence,
) -> ExperimentalWorkflowSelectedBindingEvidence:
    if type(value) is not ExperimentalWorkflowSelectedBindingEvidence:
        raise TypeError(
            "selected_binding_evidence must be "
            "ExperimentalWorkflowSelectedBindingEvidence"
        )
    reconstructed = ExperimentalWorkflowSelectedBindingEvidence(
        enablement_result=value.enablement_result,
        selection_result=value.selection_result,
    )
    if reconstructed != value:
        raise ValueError("selected binding evidence differs after validation")
    return reconstructed


def _reconstruct_coordinates(
    value: ExperimentalWorkflowFiringRequestCoordinates,
) -> ExperimentalWorkflowFiringRequestCoordinates:
    if type(value) is not ExperimentalWorkflowFiringRequestCoordinates:
        raise TypeError(
            "coordinates must be ExperimentalWorkflowFiringRequestCoordinates"
        )
    reconstructed = ExperimentalWorkflowFiringRequestCoordinates(
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        occurrence_identity=value.occurrence_identity,
        attempt_identity=value.attempt_identity,
        attempt_ordinal=value.attempt_ordinal,
    )
    if reconstructed != value:
        raise ValueError("coordinates differ after validation")
    return reconstructed


def _reconstruct_source_evidence(
    value: ExperimentalWorkflowPureActionInputSourceEvidence,
) -> ExperimentalWorkflowPureActionInputSourceEvidence:
    if type(value) is not ExperimentalWorkflowPureActionInputSourceEvidence:
        raise TypeError(
            "source_evidence must contain "
            "ExperimentalWorkflowPureActionInputSourceEvidence"
        )
    reconstructed = ExperimentalWorkflowPureActionInputSourceEvidence(
        source_kind=value.source_kind,
        source_profile_identity=value.source_profile_identity,
        source_identity=value.source_identity,
        payload=value.payload,
    )
    if reconstructed != value:
        raise ValueError("source evidence differs after validation")
    return reconstructed


def _reconstruct_payload(value: WorkflowInlinePayload) -> WorkflowInlinePayload:
    return WorkflowInlinePayload(
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


def _validate_ascii_token(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value or len(value) > 512 or value != value.strip():
        raise ValueError(f"{label} must be nonempty, bounded, and stripped")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError(f"{label} must contain ASCII only") from error
    if any(byte <= 0x20 or byte == 0x7F for byte in encoded):
        raise ValueError(f"{label} must exclude whitespace and controls")


def _validate_opaque_source_identity(value: str) -> None:
    _validate_ascii_token(value, "source identity")
    encoded = value.encode("ascii")
    if len(encoded) > _MAX_SOURCE_IDENTITY_BYTES:
        raise ValueError("source identity exceeds its byte bound")
    lowered = value.lower()
    if (
        "/" in value
        or "\\" in value
        or value in {".", ".."}
        or value.startswith(("~", "./", "../"))
        or lowered.startswith("file:")
        or re.match(r"^[A-Za-z]:[\\/]", value) is not None
    ):
        raise ValueError("source identity must not be a machine path")


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


__all__ = [
    "ExperimentalWorkflowPureActionAdmittedInputs",
    "ExperimentalWorkflowPureActionAdmittedInputsIdentity",
    "ExperimentalWorkflowPureActionInputAdmissionFactory",
    "ExperimentalWorkflowPureActionInputSourceEvidence",
    "ExperimentalWorkflowPureActionInputSourceEvidenceIdentity",
]
