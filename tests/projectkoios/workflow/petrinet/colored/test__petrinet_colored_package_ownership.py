from __future__ import annotations

import ast
from pathlib import Path

import projectkoios.workflow.petrinet.colored as colored


def test_artifact__package_initializers__do_not_aggregate_objects() -> None:
    package_root = Path(colored.__file__).parent
    for path in package_root.rglob("__init__.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(
            isinstance(
                node,
                (
                    ast.ClassDef,
                    ast.FunctionDef,
                    ast.Import,
                    ast.ImportFrom,
                ),
            )
            for node in tree.body
        ), f"package initializer aggregates objects: {path}"
        assert any(
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and isinstance(node.value, ast.Tuple)
            and not node.value.elts
            for node in tree.body
        ), f"package initializer lacks explicit empty export surface: {path}"


def test_artifact__package_ownership__has_no_flat_shims_or_import_cycles() -> (
    None
):
    package_root = Path(colored.__file__).parent
    paths = tuple(package_root.rglob("*.py"))
    relative_paths = {
        path.relative_to(package_root).as_posix() for path in paths
    }

    assert {
        "canonical/definitions.py",
        "canonical/expressions/guards.py",
        "canonical/expressions/values.py",
        "canonical/markings.py",
        "control/records/canonical.py",
        "control/records/schema.py",
        "control/records/type_graph.py",
        "shadow/firing.py",
        "shadow/replay.py",
        "validation/definitions.py",
        "validation/markings.py",
    } <= relative_paths
    assert (
        not {
            "canonical.py",
            "canonical_definition.py",
            "canonical_expressions.py",
            "canonical_marking.py",
            "control_records.py",
            "expression_operations.py",
            "expressions.py",
            "shadow.py",
            "validation.py",
            "workflow_identities.py",
        }
        & relative_paths
    )

    module_paths = {
        ".".join(path.relative_to(package_root).with_suffix("").parts).replace(
            ".__init__", ""
        ): path
        for path in paths
    }
    dependencies = {module_name: set[str]() for module_name in module_paths}
    for module_name, path in module_paths.items():
        parts = module_name.split(".") if module_name else []
        package_parts = parts if path.name == "__init__.py" else parts[:-1]
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.ImportFrom) or not node.level:
                continue
            ancestor_count = node.level - 1
            base = package_parts[: len(package_parts) - ancestor_count]
            target = ".".join(base + ([node.module] if node.module else []))
            if target in module_paths and target != module_name:
                dependencies[module_name].add(target)

    visited: set[str] = set()
    active: set[str] = set()

    def visit(module_name: str) -> None:
        if module_name in active:
            raise AssertionError(f"package import cycle at {module_name}")
        if module_name in visited:
            return
        active.add(module_name)
        for dependency in dependencies[module_name]:
            visit(dependency)
        active.remove(module_name)
        visited.add(module_name)

    for module_name in dependencies:
        visit(module_name)
