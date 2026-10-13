import pytest
from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowDomainPayloadReferenceEncodingInput,
)


def test_constructor__retains_only_exact_reference() -> None:
    source = payload_reference()
    assert (
        WorkflowDomainPayloadReferenceEncodingInput(source).reference is source
    )
    with pytest.raises(TypeError):
        WorkflowDomainPayloadReferenceEncodingInput("reference")  # type: ignore[arg-type]
