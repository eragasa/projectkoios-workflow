"""Assemble, transport, and verify an opaque retained payload reference."""

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
from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowDomainPayloadReferenceCodec,
    WorkflowDomainPayloadReferenceDecodingInput,
    WorkflowDomainPayloadReferenceEncodingInput,
)
from projectkoios.workflow.petrinet.colored.payloads.references.definition import (
    WorkflowDomainPayloadEncodingMetadata,
)
from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerificationRequest,
    WorkflowDomainPayloadReferenceVerifier,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValueKind,
)


def main() -> None:
    """Keep provider bytes opaque while verifying exact retained evidence."""
    payload = b'{"energy_rydberg":-7.5}'
    binding = WorkflowPayloadColorBinding(
        CpnDefinitionIdentity("example.definition"),
        CpnColorIdentity("simulation-result"),
        CpnValueKind.STRING,
        "example.simulations",
        "example.simulation-result:1",
        "example.simulation-result-json:1",
        "application/vnd.example.simulation-result+json",
        4096,
        1,
        True,
        1,
    )
    metadata = WorkflowDomainPayloadEncodingMetadata(
        "example.simulation-result:run-1",
        binding.payload_schema_identity,
        binding.media_type_identity,
    )
    assembled = WorkflowDomainPayloadReferenceAssembler().execute(
        WorkflowDomainPayloadReferenceAssemblyRequest(
            payload,
            metadata,
            "artifact:sha256-object/run-1",
            binding,
        )
    )
    if assembled.reference is None:
        raise RuntimeError(f"assembly failed: {assembled.failure!r}")

    codec = WorkflowDomainPayloadReferenceCodec()
    document = codec.encode(
        WorkflowDomainPayloadReferenceEncodingInput(assembled.reference)
    )
    decoded = codec.decode(
        WorkflowDomainPayloadReferenceDecodingInput(
            document,
            assembled.reference.identity,
        )
    )
    verified = WorkflowDomainPayloadReferenceVerifier().execute(
        WorkflowDomainPayloadReferenceVerificationRequest(
            decoded.reference,
            payload,
            binding,
        )
    )
    if not verified.is_verified:
        raise RuntimeError(f"verification failed: {verified.issues!r}")
    print(decoded.reference.identity.value)


if __name__ == "__main__":
    main()
