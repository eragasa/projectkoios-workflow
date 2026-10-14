import pytest

from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerificationIssue,
    WorkflowDomainPayloadReferenceVerificationIssueCode,
)


def test_constructor__requires_typed_nonempty_path() -> None:
    source = WorkflowDomainPayloadReferenceVerificationIssue(
        WorkflowDomainPayloadReferenceVerificationIssueCode.SHA256_MISMATCH,
        ("reference", "sha256"),
    )
    assert source.path[-1] == "sha256"
    with pytest.raises(TypeError):
        WorkflowDomainPayloadReferenceVerificationIssue(
            WorkflowDomainPayloadReferenceVerificationIssueCode.SHA256_MISMATCH,
            ("",),
        )
