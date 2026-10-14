"""Public API and dependency-boundary verification for workflow core."""

from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
from dataclasses import is_dataclass
from pathlib import Path

import projectkoios.workflow.core as core
from projectkoios.workflow.core.identities import definition as identities
from projectkoios.workflow.core.records.runs import WorkflowRunStarter
from projectkoios.workflow.core.transitions.execution import (
    WorkflowTransitionProcessor,
)
from projectkoios.workflow.core.transitions.replay import (
    WorkflowTransitionReplayer,
)
from projectkoios.workflow.core.transitions.validation import (
    WorkflowTransitionValidator,
)


def test__workflow_core_public_api__is_explicit() -> None:
    """The core initializer is a namespace boundary, never a facade."""
    assert core.__all__ == ()


def test__workflow_core_identity__is_stable_across_hash_seeds() -> None:
    """Content identity is independent of process hash randomization."""
    script = """
from projectkoios.workflow.core.identities.definition import (
    WorkflowOperationIdentity,
)
from projectkoios.workflow.core.records.references import (
    WorkflowDefinitionReference,
)
definition = WorkflowDefinitionReference.create(
    contract_id="test.definition",
    definition_version="1",
    definition_digest_sha256="e" * 64,
    operation_identities=(
        WorkflowOperationIdentity("second"),
        WorkflowOperationIdentity("first"),
    ),
)
print(definition.identity.value)
"""
    outputs: list[str] = []
    for seed in ("1", "777"):
        environment = os.environ.copy()
        environment["PYTHONHASHSEED"] = seed
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        outputs.append(completed.stdout.strip())

    assert outputs[0] == outputs[1]


def test__workflow_core_identity_types__remain_nominal() -> None:
    """Each domain identity is a distinct runtime type, not a string alias."""
    identity_types = [
        value
        for name, value in vars(identities).items()
        if name.startswith("Workflow")
        and name.endswith("Identity")
        and is_dataclass(value)
    ]

    assert len(identity_types) == len(set(identity_types))
    for identity_type in identity_types:
        value = identity_type("synthetic")
        assert type(value) is identity_type
        assert value.value == "synthetic"


def test__workflow_core__does_not_import_optional_engines_or_outer_layers() -> (
    None
):
    """Core modules remain independent of CPN, persistence, adapters, and UI."""
    package_dir = Path(inspect.getfile(core)).parent
    prohibited_fragments = {
        "api",
        "fastapi",
        "ingestion",
        "petrinet",
        "pydantic",
        "runtime",
        "sqlite3",
        "web",
    }
    violations: list[str] = []

    for path in sorted(package_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                modules.append(node.module)
            for module in modules:
                parts = set(module.split("."))
                if parts & prohibited_fragments:
                    violations.append(f"{path.name}:{module}")

    assert violations == []


def test__workflow_core_actions__expose_one_explicit_execute_method() -> None:
    """Actions use explicit inputs rather than hidden mutable state."""
    actions = (
        WorkflowRunStarter,
        WorkflowTransitionProcessor,
        WorkflowTransitionReplayer,
        WorkflowTransitionValidator,
    )

    for action in actions:
        public_methods = [
            name
            for name, value in inspect.getmembers(action, inspect.isfunction)
            if not name.startswith("_")
        ]
        assert public_methods == ["execute"]
