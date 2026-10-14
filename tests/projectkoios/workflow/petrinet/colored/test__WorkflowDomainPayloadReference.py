from dataclasses import fields

import pytest
from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.payloads.references.definition import (
    WorkflowDomainPayloadReference,
)


def test_constructor__derives_reference_identity_and_rejects_machine_path() -> (
    None
):
    source = payload_reference()
    assert source.identity.value.startswith(
        "projectkoios.workflow.payload-reference:1:"
    )
    assert tuple(item.name for item in fields(source)) == (
        "payload_identity",
        "schema_identity",
        "media_type",
        "sha256",
        "byte_size",
        "artifact_identity",
    )
    with pytest.raises(ValueError):
        WorkflowDomainPayloadReference(
            source.payload_identity,
            source.schema_identity,
            source.media_type,
            source.sha256,
            source.byte_size,
            "/tmp/payload",
        )
