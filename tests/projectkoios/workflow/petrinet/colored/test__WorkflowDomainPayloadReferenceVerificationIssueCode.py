from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerificationIssueCode,
)


def test_enum__is_closed_and_stable() -> None:
    assert tuple(
        item.value
        for item in WorkflowDomainPayloadReferenceVerificationIssueCode
    ) == (
        "payload_too_large",
        "byte_size_mismatch",
        "sha256_mismatch",
        "schema_mismatch",
        "media_type_mismatch",
    )
