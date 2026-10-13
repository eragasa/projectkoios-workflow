import pytest
from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.payloads.references.assembly import (
    WorkflowDomainPayloadReferenceAssemblyResult,
)


def test_constructor__requires_exactly_one_variant() -> None:
    assert (
        WorkflowDomainPayloadReferenceAssemblyResult(
            reference=payload_reference()
        ).failure
        is None
    )
    with pytest.raises(ValueError):
        WorkflowDomainPayloadReferenceAssemblyResult()
