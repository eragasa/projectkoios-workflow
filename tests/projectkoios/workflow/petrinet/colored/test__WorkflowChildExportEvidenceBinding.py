from dataclasses import replace

import pytest

from _child_export_evidence_fixtures import (
    child_export,
    child_export_evidence_binding,
    evidence_reference,
)
from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExport,
    WorkflowChildDefinitionExportIdentity,
)
from projectkoios.workflow.petrinet.colored.children.exports.evidence import (
    WorkflowChildExportEvidenceBinding,
)


def test_constructor__binds_verified_export_to_ordered_evidence() -> None:
    source = child_export_evidence_binding()
    assert source.child_export_identity == source.child_export.identity
    assert len(source.evidence_references) == 1


def test_constructor__rejects_asserted_export_identity() -> None:
    exported = child_export()
    asserted = WorkflowChildDefinitionExport(
        exported.closure,
        WorkflowChildDefinitionExportIdentity(
            "projectkoios.workflow.child-definition-export:0.1:" + "a" * 64
        ),
    )
    with pytest.raises(ValueError, match="does not match"):
        WorkflowChildExportEvidenceBinding(asserted, (evidence_reference(),), 1)


def test_constructor__rejects_duplicate_evidence_role() -> None:
    first = evidence_reference()
    second = replace(first, artifact_identity="artifact:other")
    references = tuple(sorted((first, second), key=lambda item: item.identity))
    with pytest.raises(ValueError, match="unique lexically ordered roles"):
        WorkflowChildExportEvidenceBinding(child_export(), references, 1)
