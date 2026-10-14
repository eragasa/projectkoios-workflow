from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerifierIdentity,
)


def test_constructor__identifies_version_one_verification() -> None:
    assert (
        WorkflowDomainPayloadReferenceVerifierIdentity().value
        == "projectkoios.workflow.payload-reference-verifier:1"
    )
