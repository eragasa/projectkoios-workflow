from dataclasses import replace

from _child_export_evidence_fixtures import evidence_reference


def test_identity__changes_for_evidence_artifact_digest() -> None:
    source = evidence_reference()
    changed = replace(source, artifact_sha256="a" * 64)
    assert source.identity != changed.identity
