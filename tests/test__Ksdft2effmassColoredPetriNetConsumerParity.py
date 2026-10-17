"""Read-only evidence for the first KSD Workflow migration tranche."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import projectkoios.workflow.petrinet.colored as colored

ROOT = Path(__file__).resolve().parents[1]
PARITY_PATH = (
    ROOT / "provenance" / "ksdft2effmass-colored-petri-net-consumer-parity.json"
)
SHADOW_PATH = ROOT / "provenance" / "colored-petri-net-shadow.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert type(value) is dict
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test__consumer_parity__binds_exact_read_only_migration_scope() -> None:
    parity = _load(PARITY_PATH)

    assert parity["schema_version"] == 1
    assert parity["status"] == "read-only consumer migration parity evidence"
    assert parity["source"] == {
        "repository": "https://github.com/eragasa/ksdft2effmass.git",
        "revision": "5aaff25b784c7d1bc079a3030a73be387dc11a0f",
        "branch_observed": "work/monograph-current-library-capabilities",
        "crosswalk_inventory_revision": (
            "2f30d7a37eab8306c7c17da0e2b316d63da8c74c"
        ),
        "implementation_changed_since_crosswalk": False,
        "bounded_subtrees_clean_at_observation": True,
        "whole_worktree_clean_at_observation": False,
    }
    assert parity["destination"] == {
        "repository": "https://github.com/eragasa/projectkoios-workflow.git",
        "baseline_revision": "334c6476277d5c9f1d87d44b0ccab37e41c2ec4e",
        "import_root": "projectkoios.workflow.petrinet.colored",
    }
    assert parity["license"] == {
        "byte_identical": True,
        "byte_size": 11_357,
        "destination_sha256": (
            "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"
        ),
        "expression": "Apache-2.0",
        "source_sha256": (
            "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"
        ),
    }
    assert (
        _sha256(ROOT / "LICENSE") == (parity["license"]["destination_sha256"])
    )
    assert parity["compatibility"] == {
        "dependency_pin_change_authorized": False,
        "identity_domain_prefix": "ksdft2effmass.petrinet.colored",
        "identity_domain_preserved": True,
        "legacy_route_reexports": "downstream change not yet authorized",
        "pickle_compatibility": "not claimed",
        "production_source": "byte-identical",
        "public_symbol_inventory": "exact",
        "python_module_identity": "not preserved by a re-export migration",
        "release_authorized": False,
        "wire_format": "not selected",
    }


def test__consumer_parity__matches_immutable_historical_shadow() -> None:
    parity = _load(PARITY_PATH)
    shadow = _load(SHADOW_PATH)

    assert shadow["source"]["commit"] == (
        "be70e856911456402ea2b2562cd2508d0963e4d9"
    )
    assert shadow["source"]["license"] == "Apache-2.0"
    assert shadow["destination"]["license"] == "Apache-2.0"
    expected = {
        item["destination_path"]: (
            item["source_path"],
            item["source_sha256"],
            item["destination_sha256"],
        )
        for item in shadow["production_files"]
    }
    observed = {
        item["upstream_path"]: (
            item["legacy_path"],
            item["sha256"],
            _sha256(ROOT / item["upstream_path"]),
        )
        for item in parity["modules"]
    }

    assert len(observed) == 9
    assert observed == expected
    for item in parity["modules"]:
        legacy_suffix = item["legacy_path"].removeprefix(
            "python/src/ksdft2effmass/petrinet/colored/"
        )
        upstream_suffix = item["upstream_path"].removeprefix(
            "src/python/projectkoios/workflow/petrinet/colored/"
        )
        assert legacy_suffix == upstream_suffix
        module_suffix = legacy_suffix.removesuffix(".py")
        if module_suffix == "__init__":
            module_suffix = ""
        else:
            module_suffix = f".{module_suffix}"
        assert item["legacy_import"] == (
            f"ksdft2effmass.petrinet.colored{module_suffix}"
        )
        assert item["upstream_import"] == (
            f"projectkoios.workflow.petrinet.colored{module_suffix}"
        )


def test__consumer_parity__excludes_owner_and_runtime_imports() -> None:
    parity = _load(PARITY_PATH)
    prohibited = ("ksdft2effmass", "projectkoios")

    for item in parity["modules"]:
        tree = ast.parse(
            (ROOT / item["upstream_path"]).read_text(encoding="utf-8")
        )
        absolute_imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module is not None
        }
        assert not any(name.startswith(prohibited) for name in absolute_imports)


def test__consumer_parity__binds_exact_public_symbol_inventory() -> None:
    parity = _load(PARITY_PATH)
    canonical = json.dumps(
        colored.__all__,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")

    assert parity["public_surface"] == {
        "export_count": 68,
        "canonical_export_list_sha256": (
            "c4fdd25caeb2ffe4d6b0895789d5678a36fb57c5e584a2220de554323b994b68"
        ),
    }
    assert len(colored.__all__) == 68
    assert (
        hashlib.sha256(canonical).hexdigest()
        == (parity["public_surface"]["canonical_export_list_sha256"])
    )
