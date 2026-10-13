"""Synthetic retained owner-payload reference fixtures."""

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinitionIdentity,
)
from projectkoios.workflow.petrinet.colored.payloads.bindings import (
    WorkflowPayloadColorBinding,
)
from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssembler,
    WorkflowDomainPayloadReferenceAssemblyRequest,
)
from projectkoios.workflow.petrinet.colored.payloads.references.definition import (
    WorkflowDomainPayloadEncodingMetadata,
    WorkflowDomainPayloadReference,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValueKind,
)

PAYLOAD_BYTES = b'{"value":"fixture"}'


def payload_color_binding(
    maximum_payload_bytes: int = 1024,
) -> WorkflowPayloadColorBinding:
    return WorkflowPayloadColorBinding(
        definition_identity=CpnDefinitionIdentity("definition"),
        color_identity=CpnColorIdentity("payload-reference"),
        allowed_value_kind=CpnValueKind.STRING,
        owner_identity="projectkoios.simulations",
        payload_schema_identity="projectkoios.simulations.fixture:1",
        codec_identity="projectkoios.simulations.fixture-codec:1",
        media_type_identity="application/vnd.projectkoios.fixture+json",
        maximum_payload_bytes=maximum_payload_bytes,
        maximum_reference_tokens_per_complete_marking=8,
        individual_token_identity_required=True,
        contract_version=1,
    )


def payload_encoding_metadata() -> WorkflowDomainPayloadEncodingMetadata:
    return WorkflowDomainPayloadEncodingMetadata(
        payload_identity="simulation-fixture-1",
        schema_identity="projectkoios.simulations.fixture:1",
        media_type="application/vnd.projectkoios.fixture+json",
    )


def payload_reference() -> WorkflowDomainPayloadReference:
    result = WorkflowDomainPayloadReferenceAssembler().execute(
        WorkflowDomainPayloadReferenceAssemblyRequest(
            payload_bytes=PAYLOAD_BYTES,
            encoding_metadata=payload_encoding_metadata(),
            artifact_identity="artifact:fixture:1",
            color_binding=payload_color_binding(),
        )
    )
    assert result.reference is not None
    return result.reference
