import pytest

from projectkoios.workflow.petrinet.colored.payloads.references.definition import (
    WorkflowDomainPayloadEncodingMetadata,
)


def test_constructor__admits_json_media_type_and_rejects_non_json() -> None:
    metadata = WorkflowDomainPayloadEncodingMetadata(
        "payload", "schema:1", "application/json"
    )
    assert metadata.media_type == "application/json"
    structured = WorkflowDomainPayloadEncodingMetadata(
        "payload", "schema:1", "application/problem+json"
    )
    assert structured.media_type == "application/problem+json"
    with pytest.raises(ValueError):
        WorkflowDomainPayloadEncodingMetadata(
            "payload", "schema:1", "text/plain"
        )
