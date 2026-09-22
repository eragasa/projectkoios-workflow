"""Dependency evidence for the effect-free local runtime boundary."""

from __future__ import annotations

import ast
from pathlib import Path

_RUNTIME_ROOT = (
    Path(__file__).parents[4]
    / "src"
    / "python"
    / "projectkoios"
    / "workflow"
    / "runtime"
)
_FORBIDDEN = {
    "fastapi",
    "httpx",
    "projectkoios.agent",
    "projectkoios.api",
    "projectkoios.workflow.petrinet",
    "random",
    "requests",
    "socket",
    "subprocess",
    "time",
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    return imported


def test__local_runtime__has_no_effect_or_cpn_dependencies() -> None:
    modules = {
        module
        for path in _RUNTIME_ROOT.glob("*.py")
        for module in imported_modules(path)
    }

    assert not {
        forbidden
        for forbidden in _FORBIDDEN
        if any(
            module == forbidden or module.startswith(f"{forbidden}.")
            for module in modules
        )
    }
