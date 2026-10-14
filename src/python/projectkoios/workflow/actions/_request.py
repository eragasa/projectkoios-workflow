"""Experimental SDK-request construction from selected CPN bindings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from projectkoios.workflow_sdk.firing import (
    WorkflowFirerDescriptor,
    WorkflowFiringRequest,
    WorkflowOccurrenceContext,
    WorkflowTransitionFirerBinding,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowAttemptIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
    WorkflowOccurrenceIdentity,
)
from projectkoios.workflow_sdk.payloads import WorkflowInlinePayload
from projectkoios.workflow_sdk.serialization import (
    WorkflowFiringRequestJsonCodec,
)

from ._selection import ExperimentalWorkflowSelectedBindingEvidence
from ._validation import (
    _round_trip_firer_descriptor,
    _round_trip_transition_binding,
    _validate_payloads,
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowFiringRequestCoordinates:
    """Retain exact runtime coordinates excluding the derived binding digest."""

    net_instance_identity: WorkflowNetInstanceIdentity
    predecessor_marking_identity: WorkflowMarkingIdentity
    predecessor_revision: int
    occurrence_identity: WorkflowOccurrenceIdentity
    attempt_identity: WorkflowAttemptIdentity
    attempt_ordinal: int

    def __post_init__(self) -> None:
        expected = (
            (
                "net_instance_identity",
                self.net_instance_identity,
                WorkflowNetInstanceIdentity,
            ),
            (
                "predecessor_marking_identity",
                self.predecessor_marking_identity,
                WorkflowMarkingIdentity,
            ),
            (
                "occurrence_identity",
                self.occurrence_identity,
                WorkflowOccurrenceIdentity,
            ),
            (
                "attempt_identity",
                self.attempt_identity,
                WorkflowAttemptIdentity,
            ),
        )
        for name, value, nominal_type in expected:
            if type(value) is not nominal_type:
                raise TypeError(f"{name} must be {nominal_type.__name__}")
        for name in ("predecessor_revision", "attempt_ordinal"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")


@final
class ExperimentalWorkflowFiringRequestFactory:
    """Construct one exact SDK request without accepting a claimed digest."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowFiringRequestFactory is not subclassable"
        )

    def execute(
        self,
        *,
        transition_binding: WorkflowTransitionFirerBinding,
        firer_descriptor: WorkflowFirerDescriptor,
        selected_binding_evidence: ExperimentalWorkflowSelectedBindingEvidence,
        coordinates: ExperimentalWorkflowFiringRequestCoordinates,
        inputs: tuple[WorkflowInlinePayload, ...],
    ) -> WorkflowFiringRequest:
        """Derive the binding digest and return a canonical SDK request."""
        if type(transition_binding) is not WorkflowTransitionFirerBinding:
            raise TypeError(
                "transition_binding must be WorkflowTransitionFirerBinding"
            )
        if type(firer_descriptor) is not WorkflowFirerDescriptor:
            raise TypeError("firer_descriptor must be WorkflowFirerDescriptor")
        if (
            type(selected_binding_evidence)
            is not ExperimentalWorkflowSelectedBindingEvidence
        ):
            raise TypeError(
                "selected_binding_evidence must be "
                "ExperimentalWorkflowSelectedBindingEvidence"
            )
        validated_selected_binding_evidence = (
            ExperimentalWorkflowSelectedBindingEvidence(
                enablement_result=selected_binding_evidence.enablement_result,
                selection_result=selected_binding_evidence.selection_result,
            )
        )
        if validated_selected_binding_evidence != selected_binding_evidence:
            raise ValueError(
                "selected binding evidence differs after validation"
            )
        selected_binding_evidence = validated_selected_binding_evidence
        if (
            type(coordinates)
            is not ExperimentalWorkflowFiringRequestCoordinates
        ):
            raise TypeError(
                "coordinates must be experimental firing request coordinates"
            )
        validated_coordinates = ExperimentalWorkflowFiringRequestCoordinates(
            net_instance_identity=coordinates.net_instance_identity,
            predecessor_marking_identity=coordinates.predecessor_marking_identity,
            predecessor_revision=coordinates.predecessor_revision,
            occurrence_identity=coordinates.occurrence_identity,
            attempt_identity=coordinates.attempt_identity,
            attempt_ordinal=coordinates.attempt_ordinal,
        )
        if validated_coordinates != coordinates:
            raise ValueError("coordinates differ after validation")

        binding = _round_trip_transition_binding(transition_binding)
        descriptor = _round_trip_firer_descriptor(firer_descriptor)
        if binding != transition_binding:
            raise ValueError(
                "transition binding differs after canonical round trip"
            )
        if descriptor != firer_descriptor:
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
        selected_binding = selected_binding_evidence.selected_binding
        if (
            selected_binding_evidence.enablement_result.definition_identity.value
            != binding.definition_identity.value
        ):
            raise ValueError("selected CPN evidence has the wrong definition")
        if selected_binding.transition_identity.value != (
            binding.transition_identity.value
        ):
            raise ValueError("selected CPN binding has the wrong transition")
        if (
            selected_binding_evidence.enablement_result.marking_identity.value
            != coordinates.predecessor_marking_identity.value
        ):
            raise ValueError(
                "selected CPN evidence has the wrong predecessor marking"
            )

        _validate_payloads(inputs, descriptor.input_contracts, "request inputs")
        input_bytes = sum(item.byte_length for item in inputs)
        if len(inputs) > descriptor.bounds.maximum_input_count:
            raise ValueError("request input count exceeds descriptor bounds")
        if input_bytes > descriptor.bounds.maximum_input_bytes:
            raise ValueError("request input bytes exceed descriptor bounds")
        if input_bytes > descriptor.bounds.maximum_total_bytes:
            raise ValueError(
                "request input bytes exceed descriptor total bound"
            )

        selected_binding_sha256 = (
            selected_binding_evidence.selected_binding_sha256
        )
        context = WorkflowOccurrenceContext(
            definition_identity=binding.definition_identity,
            net_instance_identity=coordinates.net_instance_identity,
            transition_identity=binding.transition_identity,
            predecessor_marking_identity=(
                coordinates.predecessor_marking_identity
            ),
            predecessor_revision=coordinates.predecessor_revision,
            selected_binding_sha256=selected_binding_sha256,
            occurrence_identity=coordinates.occurrence_identity,
            attempt_identity=coordinates.attempt_identity,
            attempt_ordinal=coordinates.attempt_ordinal,
        )
        request = WorkflowFiringRequest(
            context=context,
            binding_identity=binding.identity,
            firer_identity=binding.firer_identity,
            inputs=inputs,
        )
        codec = WorkflowFiringRequestJsonCodec()
        validated_request = codec.decode(codec.encode(request))
        if validated_request != request:
            raise ValueError("request differs after canonical round trip")
        return request


__all__ = [
    "ExperimentalWorkflowFiringRequestCoordinates",
    "ExperimentalWorkflowFiringRequestFactory",
]
