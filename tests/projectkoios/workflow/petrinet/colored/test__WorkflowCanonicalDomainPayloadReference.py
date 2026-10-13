from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowCanonicalDomainPayloadReference,
    WorkflowDomainPayloadReferenceCodec,
    WorkflowDomainPayloadReferenceEncodingInput,
)


def test_constructor__derives_exact_byte_correlations() -> None:
    reference = payload_reference()
    document = WorkflowDomainPayloadReferenceCodec().encode(
        WorkflowDomainPayloadReferenceEncodingInput(reference)
    )
    assert isinstance(document, WorkflowCanonicalDomainPayloadReference)
    assert document.identity == reference.identity
    assert document.representation_profile_identity.endswith(":1")
