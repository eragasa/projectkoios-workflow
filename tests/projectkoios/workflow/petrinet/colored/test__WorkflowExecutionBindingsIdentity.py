import pytest

from projectkoios.workflow.petrinet.colored.deployments.bindings import (
    WorkflowExecutionBindingsIdentity,
)


def test_constructor__accepts_exact_domain_separated_digest() -> None:
    value = "projectkoios.workflow.execution-bindings:0.1:" + "a" * 64
    assert WorkflowExecutionBindingsIdentity(value).value == value


def test_constructor__rejects_non_digest_label() -> None:
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        WorkflowExecutionBindingsIdentity(
            "projectkoios.workflow.execution-bindings:0.1:not-a-digest"
        )
