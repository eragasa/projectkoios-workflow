from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
MANIFEST_PATH = ROOT / "provenance" / "colored-petri-net-shadow.json"
SOURCE_DIRECTORY = ROOT / "src/python/projectkoios/workflow/petrinet/colored"
TEST_DIRECTORY = ROOT / "tests/projectkoios/workflow/petrinet/colored"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test__shadow_manifest__binds_exact_source_revision_and_boundaries() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())

    assert manifest["schema_version"] == 1
    assert manifest["pilot"] == "WORKFLOW-CPN-SHADOW-01"
    assert manifest["source"]["commit"] == (
        "be70e856911456402ea2b2562cd2508d0963e4d9"
    )
    assert manifest["source"]["license"] == "Apache-2.0"
    assert manifest["destination"]["python_target"] == ">=3.14"
    assert manifest["compatibility"]["claim"] == "none"
    assert manifest["compatibility"]["wire_format"] == "not selected"
    assert manifest["compatibility"]["legacy_identity_domains_preserved"]


def test__shadow_manifest__binds_byte_identical_production_source() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    records = manifest["production_files"]

    assert {path.name for path in SOURCE_DIRECTORY.glob("*.py")} == {
        Path(record["destination_path"]).name for record in records
    }
    for record in records:
        path = ROOT / record["destination_path"]
        assert record["transformation"] == "byte-identical"
        assert record["source_sha256"] == record["destination_sha256"]
        assert _sha256(path) == record["destination_sha256"]


def test__shadow_manifest__binds_transformed_software_verification() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    records = manifest["test_files"]

    assert {path.name for path in TEST_DIRECTORY.glob("*.py")} == {
        Path(record["destination_path"]).name for record in records
    }
    for record in records:
        path = ROOT / record["destination_path"]
        assert _sha256(path) == record["destination_sha256"]
        assert record["transformation"] in {
            "namespace substitution only",
            (
                "namespace substitution and Project Koios "
                "dependency-boundary adaptation"
            ),
        }
