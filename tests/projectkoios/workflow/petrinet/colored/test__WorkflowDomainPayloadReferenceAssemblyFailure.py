import pytest

from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssemblyFailure,
    WorkflowDomainPayloadReferenceAssemblyFailureCode,
)


def test_constructor__requires_typed_nonempty_diagnostic() -> None:
    source = WorkflowDomainPayloadReferenceAssemblyFailure(
        WorkflowDomainPayloadReferenceAssemblyFailureCode.EMPTY_PAYLOAD,
        ("payload_bytes",),
        "empty",
    )
    assert source.path == ("payload_bytes",)
    with pytest.raises(TypeError):
        WorkflowDomainPayloadReferenceAssemblyFailure(
            WorkflowDomainPayloadReferenceAssemblyFailureCode.EMPTY_PAYLOAD,
            (),
            "",
        )
