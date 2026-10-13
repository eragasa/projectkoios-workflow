from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssemblyFailureCode,
)


def test_enum__is_closed_and_stable() -> None:
    assert tuple(
        item.value for item in WorkflowDomainPayloadReferenceAssemblyFailureCode
    ) == (
        "empty_payload",
        "payload_too_large",
        "schema_mismatch",
        "media_type_mismatch",
        "invalid_artifact_identity",
    )
