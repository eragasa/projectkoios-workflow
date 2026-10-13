import pytest
from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowDomainPayloadReferenceDecodingResult,
)


def test_constructor__retains_only_exact_reference() -> None:
    reference = payload_reference()
    assert (
        WorkflowDomainPayloadReferenceDecodingResult(reference).reference
        is reference
    )
    with pytest.raises(TypeError):
        WorkflowDomainPayloadReferenceDecodingResult("reference")  # type: ignore[arg-type]
