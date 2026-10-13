from dataclasses import replace
from _payload_reference_fixtures import (
    PAYLOAD_BYTES,
    payload_color_binding,
    payload_reference,
)

from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerificationIssueCode,
    WorkflowDomainPayloadReferenceVerificationRequest,
    WorkflowDomainPayloadReferenceVerifier,
)


def test_method__execute__verifies_exact_bytes_and_reports_substitution() -> (
    None
):
    request = WorkflowDomainPayloadReferenceVerificationRequest(
        payload_reference(), PAYLOAD_BYTES, payload_color_binding()
    )
    assert WorkflowDomainPayloadReferenceVerifier().execute(request).is_verified
    changed = WorkflowDomainPayloadReferenceVerifier().execute(
        replace(request, payload_bytes=PAYLOAD_BYTES + b"!")
    )
    assert tuple(item.code for item in changed.issues) == (
        WorkflowDomainPayloadReferenceVerificationIssueCode.BYTE_SIZE_MISMATCH,
        WorkflowDomainPayloadReferenceVerificationIssueCode.SHA256_MISMATCH,
    )
    changed_contract = WorkflowDomainPayloadReferenceVerifier().execute(
        replace(
            request,
            reference=replace(
                request.reference,
                schema_identity="projectkoios.simulations.other:1",
                media_type="application/vnd.projectkoios.other+json",
            ),
        )
    )
    assert tuple(item.code for item in changed_contract.issues) == (
        WorkflowDomainPayloadReferenceVerificationIssueCode.SCHEMA_MISMATCH,
        WorkflowDomainPayloadReferenceVerificationIssueCode.MEDIA_TYPE_MISMATCH,
    )
