import pytest
from _payload_reference_fixtures import (
    PAYLOAD_BYTES,
    payload_color_binding,
    payload_reference,
)

from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerificationRequest,
)


def test_constructor__retains_complete_correlation_input() -> None:
    source = WorkflowDomainPayloadReferenceVerificationRequest(
        payload_reference(), PAYLOAD_BYTES, payload_color_binding()
    )
    assert source.payload_bytes == PAYLOAD_BYTES
    with pytest.raises(TypeError):
        WorkflowDomainPayloadReferenceVerificationRequest(
            payload_reference(), "bytes", payload_color_binding()
        )  # type: ignore[arg-type]
