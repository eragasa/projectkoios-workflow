"""Architecture evidence for the canonical durable pure-action write path."""

from __future__ import annotations

import ast
from pathlib import Path

from projectkoios.workflow.execution import (
    ExperimentalWorkflowPureActionCommitService,
    ExperimentalWorkflowPureActionDurableCpnCommitService,
)

_EXECUTION_ROOT = (
    Path(__file__).parents[4]
    / "src"
    / "python"
    / "projectkoios"
    / "workflow"
    / "execution"
)
_COMPACT_SERVICE = "ExperimentalWorkflowPureActionCommitService"


def test_compact_only_writer_remains_an_explicit_compatibility_export() -> None:
    assert ExperimentalWorkflowPureActionCommitService.__module__.endswith(
        ".pure_action_commit"
    )
    durable_module = (
        ExperimentalWorkflowPureActionDurableCpnCommitService.__module__
    )
    assert durable_module.endswith(".pure_action_durable_cpn_commit")
    assert "Compatibility writer" in (
        ExperimentalWorkflowPureActionCommitService.__doc__ or ""
    )


def test_production_execution_modules_do_not_call_compact_only_writer() -> None:
    callers = []
    for path in _EXECUTION_ROOT.glob("*.py"):
        if path.name == "pure_action_commit.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            called_name = None
            if isinstance(function, ast.Name):
                called_name = function.id
            elif isinstance(function, ast.Attribute):
                called_name = function.attr
            if called_name == _COMPACT_SERVICE:
                callers.append(f"{path.name}:{node.lineno}")

    assert callers == []
