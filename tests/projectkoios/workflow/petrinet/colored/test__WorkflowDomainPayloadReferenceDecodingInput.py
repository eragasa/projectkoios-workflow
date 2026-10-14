import pytest
from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowDomainPayloadReferenceCodec,
    WorkflowDomainPayloadReferenceDecodingInput,
    WorkflowDomainPayloadReferenceEncodingInput,
)


def test_constructor__retains_document_and_claimed_identity() -> None:
    reference = payload_reference()
    document = WorkflowDomainPayloadReferenceCodec().encode(
        WorkflowDomainPayloadReferenceEncodingInput(reference)
    )
    source = WorkflowDomainPayloadReferenceDecodingInput(
        document, reference.identity
    )
    assert source.claimed_identity == document.identity
    with pytest.raises(TypeError):
        WorkflowDomainPayloadReferenceDecodingInput(document, "identity")  # type: ignore[arg-type]
