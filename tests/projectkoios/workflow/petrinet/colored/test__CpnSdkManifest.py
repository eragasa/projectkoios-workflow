"""Mechanical stability gate for the human/LLM SDK manifest."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_manifest__matches_public_operations_and_signatures(
    pytestconfig: pytest.Config,
) -> None:
    """The checked-in discovery surface must match importable SDK types."""
    root = Path(str(pytestconfig.rootpath))
    result = subprocess.run(
        (
            sys.executable,
            str(root / "tools/generate_cpn_sdk_manifest.py"),
            "--check",
            "--root",
            str(root),
        ),
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_manifest__is_task_discoverable_and_release_candidate(
    pytestconfig: pytest.Config,
) -> None:
    """Each operation names its module, identity, typed boundary, and status."""
    root = Path(str(pytestconfig.rootpath))
    manifest = json.loads(
        (root / "docs/sdk/operation-manifest.json").read_text()
    )
    assert manifest["contract_namespace"] == "projectkoios/workflow/v0.1"
    assert manifest["stability"] == "release-candidate"
    assert len(manifest["operations"]) >= 50
    assert len(manifest["public_types"]) >= 350
    assert len(manifest["tasks"]) == 5
    operation_names = {
        operation["action"] for operation in manifest["operations"]
    }
    for task in manifest["tasks"]:
        assert task["task"]
        assert (root / task["example"]).is_file()
        assert set(task["operations"]) <= operation_names
    enums = [
        public_type
        for public_type in manifest["public_types"]
        if public_type["kind"] == "enum"
    ]
    assert enums
    assert all(public_type["members"] for public_type in enums)
    for operation in manifest["operations"]:
        assert operation["module"].startswith(
            "projectkoios.workflow.petrinet.colored."
        )
        assert isinstance(operation["identity"], str)
        assert operation["identity"]
        assert operation["stability"] == "release-candidate"
        assert operation["methods"]
        for method in operation["methods"]:
            assert method["request_types"]
            assert all(method["request_types"])
            assert method["response_type"]
