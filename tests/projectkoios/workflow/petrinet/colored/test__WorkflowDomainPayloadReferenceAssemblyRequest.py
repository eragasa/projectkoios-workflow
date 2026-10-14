from dataclasses import fields
from _payload_reference_fixtures import (
    PAYLOAD_BYTES,
    payload_color_binding,
    payload_encoding_metadata,
)

from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssemblyRequest,
)


def test_constructor__has_no_claimed_digest_or_size() -> None:
    source = WorkflowDomainPayloadReferenceAssemblyRequest(
        PAYLOAD_BYTES,
        payload_encoding_metadata(),
        "artifact:1",
        payload_color_binding(),
    )
    assert tuple(item.name for item in fields(source)) == (
        "payload_bytes",
        "encoding_metadata",
        "artifact_identity",
        "color_binding",
    )
