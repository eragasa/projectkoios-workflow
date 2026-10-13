import pytest

from projectkoios.workflow.petrinet.colored.payloads.references.verification import (
    WorkflowDomainPayloadReferenceVerificationIssue,
    WorkflowDomainPayloadReferenceVerificationIssueCode,
    WorkflowDomainPayloadReferenceVerificationResult,
)


def test_constructor__reports_verified_only_without_issues() -> None:
    assert WorkflowDomainPayloadReferenceVerificationResult(()).is_verified
    issue = WorkflowDomainPayloadReferenceVerificationIssue(
        WorkflowDomainPayloadReferenceVerificationIssueCode.SHA256_MISMATCH,
        ("sha256",),
    )
    assert not WorkflowDomainPayloadReferenceVerificationResult(
        (issue,)
    ).is_verified
    with pytest.raises(ValueError):
        WorkflowDomainPayloadReferenceVerificationResult((issue, issue))
