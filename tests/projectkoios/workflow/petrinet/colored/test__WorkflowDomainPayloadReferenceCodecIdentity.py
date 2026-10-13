from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowDomainPayloadReferenceCodecIdentity,
)


def test_constructor__identifies_version_one_transport() -> None:
    assert (
        WorkflowDomainPayloadReferenceCodecIdentity().value
        == "projectkoios.workflow.payload-reference-codec:1"
    )
