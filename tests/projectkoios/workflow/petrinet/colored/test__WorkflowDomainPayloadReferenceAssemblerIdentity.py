from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssemblerIdentity,
)


def test_constructor__identifies_version_one_assembly() -> None:
    assert (
        WorkflowDomainPayloadReferenceAssemblerIdentity().value
        == "projectkoios.workflow.payload-reference-assembler:1"
    )
