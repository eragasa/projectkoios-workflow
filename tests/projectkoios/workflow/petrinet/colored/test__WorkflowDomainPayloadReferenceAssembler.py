from dataclasses import replace
from _payload_reference_fixtures import (
    PAYLOAD_BYTES,
    payload_color_binding,
    payload_encoding_metadata,
)

from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssembler,
    WorkflowDomainPayloadReferenceAssemblyFailureCode,
    WorkflowDomainPayloadReferenceAssemblyRequest,
)


def test_method__execute__derives_correlations_and_closes_failures() -> None:
    request = WorkflowDomainPayloadReferenceAssemblyRequest(
        PAYLOAD_BYTES,
        payload_encoding_metadata(),
        "artifact:1",
        payload_color_binding(),
    )
    success = WorkflowDomainPayloadReferenceAssembler().execute(request)
    assert success.reference is not None
    assert success.reference.byte_size == len(PAYLOAD_BYTES)
    assert success.reference.sha256 not in ("", "0" * 64)
    empty = WorkflowDomainPayloadReferenceAssembler().execute(
        replace(request, payload_bytes=b"")
    )
    assert empty.failure is not None
    assert (
        empty.failure.code
        is WorkflowDomainPayloadReferenceAssemblyFailureCode.EMPTY_PAYLOAD
    )
    oversized = WorkflowDomainPayloadReferenceAssembler().execute(
        replace(request, color_binding=payload_color_binding(1))
    )
    assert oversized.failure is not None
    assert (
        oversized.failure.code
        is WorkflowDomainPayloadReferenceAssemblyFailureCode.PAYLOAD_TOO_LARGE
    )
    wrong_schema = WorkflowDomainPayloadReferenceAssembler().execute(
        replace(
            request,
            encoding_metadata=replace(
                payload_encoding_metadata(),
                schema_identity="projectkoios.simulations.other:1",
            ),
        )
    )
    assert wrong_schema.failure is not None
    assert (
        wrong_schema.failure.code
        is WorkflowDomainPayloadReferenceAssemblyFailureCode.SCHEMA_MISMATCH
    )
    path = WorkflowDomainPayloadReferenceAssembler().execute(
        replace(request, artifact_identity="/tmp/payload")
    )
    assert path.failure is not None
    assert (
        path.failure.code
        is WorkflowDomainPayloadReferenceAssemblyFailureCode.INVALID_ARTIFACT_IDENTITY
    )
