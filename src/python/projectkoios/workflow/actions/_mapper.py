"""Pure executor for the experimental ASCII output mapping."""

from __future__ import annotations

from typing import final

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)
from projectkoios.workflow_sdk.firing import (
    WorkflowFiringRequest,
    WorkflowFiringSucceeded,
    WorkflowOccurrenceContext,
)
from projectkoios.workflow_sdk.serialization import (
    WorkflowFiringRequestJsonCodec,
    WorkflowFiringResultJsonCodec,
)

from ._models import (
    ExperimentalWorkflowAsciiOutputMappingDescriptor,
    ExperimentalWorkflowMappedActionResult,
)
from ._validation import (
    _decode_path_free_ascii_identity,
    _validate_bounds,
    _validate_payloads,
)


@final
class ExperimentalWorkflowAsciiOutputMapper:
    """Validate and map one exact SDK success without owner-domain imports."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowAsciiOutputMapper is not subclassable"
        )

    def execute(
        self,
        *,
        mapping: ExperimentalWorkflowAsciiOutputMappingDescriptor,
        transition: ColoredPetriNetTransitionDefinition,
        expected_context: WorkflowOccurrenceContext,
        request: WorkflowFiringRequest,
        result: WorkflowFiringSucceeded,
    ) -> ExperimentalWorkflowMappedActionResult:
        """Return an identity-bound candidate external-output binding.

        ``expected_context`` is the exact retained reservation context supplied
        by the outer runtime. This method checks equality but does not read or
        revalidate a current marking and does not fire the CPN.
        """
        if (
            type(mapping)
            is not ExperimentalWorkflowAsciiOutputMappingDescriptor
        ):
            raise TypeError(
                "mapping must be an experimental ASCII output "
                "mapping descriptor"
            )
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
            raise ValueError("mapping differs from its content identity")
        if type(transition) is not ColoredPetriNetTransitionDefinition:
            raise TypeError(
                "transition must be ColoredPetriNetTransitionDefinition"
            )
        if type(expected_context) is not WorkflowOccurrenceContext:
            raise TypeError(
                "expected_context must be WorkflowOccurrenceContext"
            )
        validated_context = WorkflowOccurrenceContext(
            definition_identity=expected_context.definition_identity,
            net_instance_identity=expected_context.net_instance_identity,
            transition_identity=expected_context.transition_identity,
            predecessor_marking_identity=expected_context.predecessor_marking_identity,
            predecessor_revision=expected_context.predecessor_revision,
            selected_binding_sha256=expected_context.selected_binding_sha256,
            occurrence_identity=expected_context.occurrence_identity,
            attempt_identity=expected_context.attempt_identity,
            attempt_ordinal=expected_context.attempt_ordinal,
        )
        if validated_context != expected_context:
            raise ValueError("expected_context differs after validation")
        if type(request) is not WorkflowFiringRequest:
            raise TypeError("request must be WorkflowFiringRequest")
        validated_request = WorkflowFiringRequestJsonCodec().decode(
            WorkflowFiringRequestJsonCodec().encode(request)
        )
        if validated_request != request:
            raise ValueError("request differs after canonical round trip")
        if type(result) is not WorkflowFiringSucceeded:
            raise TypeError("result must be WorkflowFiringSucceeded")
        validated_result = WorkflowFiringResultJsonCodec().decode(
            WorkflowFiringResultJsonCodec().encode(result)
        )
        if type(validated_result) is not WorkflowFiringSucceeded:
            raise ValueError("result canonical round trip changed its variant")
        if validated_result != result:
            raise ValueError("result differs after canonical round trip")

        binding = mapping.transition_binding
        descriptor = mapping.firer_descriptor
        if request.context != expected_context:
            raise ValueError(
                "request context differs from retained expectation"
            )
        if request.binding_identity != binding.identity:
            raise ValueError("request binding identity differs from mapping")
        if request.firer_identity != descriptor.identity:
            raise ValueError("request firer identity differs from mapping")
        if request.context.definition_identity != binding.definition_identity:
            raise ValueError("request definition identity differs from mapping")
        if request.context.transition_identity != binding.transition_identity:
            raise ValueError("request transition identity differs from mapping")
        if transition.identity.value != binding.transition_identity.value:
            raise ValueError("CPN transition identity differs from mapping")
        if transition.external_output_variable_identities != (
            mapping.external_variable_identity,
        ):
            raise ValueError(
                "CPN transition external variables differ from scalar mapping"
            )

        if result.request_identity != request.identity:
            raise ValueError("result request identity differs from request")
        if result.occurrence_identity != request.context.occurrence_identity:
            raise ValueError("result occurrence identity differs from request")
        if result.attempt_identity != request.context.attempt_identity:
            raise ValueError("result attempt identity differs from request")
        if result.firer_identity != request.firer_identity:
            raise ValueError("result firer identity differs from request")

        _validate_payloads(
            request.inputs,
            descriptor.input_contracts,
            "request inputs",
        )
        _validate_payloads(
            result.outputs,
            descriptor.output_contracts,
            "result outputs",
        )
        _validate_payloads(
            result.evidence,
            descriptor.evidence_contracts,
            "result evidence",
        )
        _validate_bounds(descriptor, request, result)

        source_output = result.outputs[0]
        identity_text = _decode_path_free_ascii_identity(
            source_output.payload,
            mapping.output_contract.maximum_byte_length,
        )
        external_output_binding = ColoredPetriNetBinding(
            transition_identity=ColoredPetriNetTransitionIdentity(
                binding.transition_identity.value
            ),
            assignments=(
                ColoredPetriNetBindingAssignment(
                    variable_identity=mapping.external_variable_identity,
                    value=ColoredPetriNetValue(
                        kind=ColoredPetriNetValueKind.STRING,
                        value=identity_text,
                    ),
                ),
            ),
        )
        return ExperimentalWorkflowMappedActionResult(
            mapping_descriptor=mapping,
            request_identity=request.identity,
            result_identity=result.identity,
            external_output_binding=external_output_binding,
            source_output=source_output,
            evidence=result.evidence,
        )


__all__ = ["ExperimentalWorkflowAsciiOutputMapper"]
