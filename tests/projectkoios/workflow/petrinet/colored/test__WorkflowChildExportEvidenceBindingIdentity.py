from _child_export_evidence_fixtures import child_export_evidence_binding


def test_identity__uses_child_export_evidence_domain() -> None:
    assert child_export_evidence_binding().identity.value.startswith(
        "projectkoios.workflow.child-export-evidence-binding:0.1:"
    )
