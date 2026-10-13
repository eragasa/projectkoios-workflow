import pytest

from projectkoios.workflow.petrinet.colored.payloads.references.definition import (
    WorkflowDomainPayloadReferenceIdentity,
)


def test_constructor__requires_domain_separated_lowercase_sha256() -> None:
    valid = WorkflowDomainPayloadReferenceIdentity(
        "projectkoios.workflow.payload-reference:1:" + "a" * 64
    )
    assert valid.value.endswith("a" * 64)
    with pytest.raises(ValueError):
        WorkflowDomainPayloadReferenceIdentity("a" * 64)
