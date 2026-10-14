from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

_CPN_ARCHITECTURE_TESTS = (
    Path("tests/architecture/test__cpn_architecture_documentation.py"),
    Path("tests/architecture/test__cpn_public_surface.py"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(root: Path) -> dict[str, object]:
    return json.loads(
        (root / "provenance/colored-petri-net-shadow.json").read_text()
    )


def test__shadow_manifest__binds_exact_source_revision_and_boundaries(
    pytestconfig: pytest.Config,
) -> None:
    manifest = _manifest(pytestconfig.rootpath)

    assert manifest["schema_version"] == 1
    assert manifest["pilot"] == "WORKFLOW-CPN-SHADOW-01"
    source = manifest["source"]
    assert isinstance(source, dict)
    assert source["commit"] == "be70e856911456402ea2b2562cd2508d0963e4d9"
    assert source["license"] == "Apache-2.0"
    destination = manifest["destination"]
    assert isinstance(destination, dict)
    assert destination["python_target"] == ">=3.14"
    compatibility = manifest["compatibility"]
    assert isinstance(compatibility, dict)
    assert compatibility["claim"] == "none"
    assert compatibility["wire_format"] == "not selected"
    assert not compatibility["legacy_identity_domains_preserved"]
    assert compatibility["identity_domain_prefix"] == (
        "projectkoios.workflow.cpn"
    )


def test__shadow_manifest__binds_pinned_source_and_owner_extensions(
    pytestconfig: pytest.Config,
) -> None:
    root = pytestconfig.rootpath
    manifest = _manifest(root)
    records = manifest["production_files"]
    owner_records = manifest["owner_production_files"]
    assert isinstance(records, list)
    assert isinstance(owner_records, list)

    recorded = {record["destination_path"] for record in records} | {
        record["path"] for record in owner_records
    }
    source_directory = (
        root / "src/python/projectkoios/workflow/petrinet/colored"
    )
    actual = {
        str(path.relative_to(root)) for path in source_directory.rglob("*.py")
    }
    assert recorded == actual
    for record in owner_records:
        path = root / record["path"]
        assert record["origin"] == "owner-authored"
        assert _sha256(path) == record["sha256"]
    for record in records:
        path = root / record["destination_path"]
        assert record["transformation"] in {
            "byte-identical",
            "owner extension after pinned byte-identical shadow import",
            "operation-package split after pinned transformed import",
        }
        if record["transformation"] == "byte-identical":
            assert record["source_sha256"] == record["destination_sha256"]
        assert _sha256(path) == record["destination_sha256"]


def test__shadow_manifest__binds_transformed_software_verification(
    pytestconfig: pytest.Config,
) -> None:
    root = pytestconfig.rootpath
    manifest = _manifest(root)
    records = manifest["test_files"]
    owner_records = manifest["owner_test_files"]
    assert isinstance(records, list)
    assert isinstance(owner_records, list)

    recorded = {record["destination_path"] for record in records} | {
        record["path"] for record in owner_records
    }
    test_directory = root / "tests/projectkoios/workflow/petrinet/colored"
    actual_paths = (
        tuple(test_directory.rglob("*.py"))
        + tuple(root / path for path in _CPN_ARCHITECTURE_TESTS)
        + (Path(__file__),)
    )
    # Purpose: consolidated CPN architecture gates remain part of the exact
    # shadow evidence even though their long-term owner is tests/architecture.
    actual = {str(path.relative_to(root)) for path in actual_paths}
    assert recorded == actual
    for record in owner_records:
        path = root / record["path"]
        assert record["origin"] == "owner-authored"
        assert _sha256(path) == record["sha256"]
    for record in records:
        path = root / record["destination_path"]
        assert _sha256(path) == record["destination_sha256"]
        assert record["transformation"] in {
            "namespace substitution only",
            (
                "namespace substitution and Project Koios "
                "dependency-boundary adaptation"
            ),
            "owner contract extension after pinned transformed import",
        }
