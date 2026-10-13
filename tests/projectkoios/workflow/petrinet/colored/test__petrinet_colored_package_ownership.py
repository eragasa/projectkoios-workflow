from __future__ import annotations

import ast
from pathlib import Path

import projectkoios.workflow.petrinet.colored as colored


def test_artifact__package_initializers__do_not_aggregate_objects() -> None:
    package_root = Path(colored.__file__).parent
    for path in package_root.rglob("__init__.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert len(tree.body) == 2, (
            f"package initializer contains statements beyond its boundary: {path}"
        )
        documentation, export_surface = tree.body
        assert (
            isinstance(documentation, ast.Expr)
            and isinstance(documentation.value, ast.Constant)
            and type(documentation.value.value) is str
        ), f"package initializer lacks its sole module docstring: {path}"
        assert (
            isinstance(export_surface, ast.AnnAssign)
            and isinstance(export_surface.target, ast.Name)
            and export_surface.target.id == "__all__"
            and isinstance(export_surface.value, ast.Tuple)
            and not export_surface.value.elts
        ), f"package initializer lacks its sole empty export surface: {path}"


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
            "enablement.py",
            "expression_operations.py",
            "expressions.py",
            "firing.py",
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

    expected_operation_dependencies = {
        "enablement.outcomes": set(),
        "enablement.identity_derivation": {"enablement.outcomes"},
        "enablement.failure_building": {
            "enablement.identity_derivation",
            "enablement.outcomes",
        },
        "enablement.ordering": {"enablement.outcomes"},
        "enablement.transitions": {
            "enablement.failure_building",
            "enablement.identity_derivation",
            "enablement.ordering",
            "enablement.outcomes",
        },
        "firing.inputs": {"enablement.outcomes"},
        "firing.audits": set(),
        "firing.outcomes": {"firing.audits", "firing.inputs"},
        "firing.occurrence_reconstruction": {"firing.audits"},
        "firing.identity_derivation": {
            "firing.audits",
            "firing.inputs",
            "firing.outcomes",
        },
        "firing.successor_marking": {"firing.audits", "firing.inputs"},
        "firing.failure_building": {
            "firing.identity_derivation",
            "firing.inputs",
            "firing.outcomes",
        },
        "firing.transitions": {
            "enablement.transitions",
            "firing.audits",
            "firing.failure_building",
            "firing.identity_derivation",
            "firing.inputs",
            "firing.occurrence_reconstruction",
            "firing.outcomes",
            "firing.successor_marking",
        },
    }
    for (
        module_name,
        expected_dependencies,
    ) in expected_operation_dependencies.items():
        actual_dependencies = {
            dependency
            for dependency in dependencies[module_name]
            if dependency.startswith(("enablement.", "firing."))
        }
        assert actual_dependencies == expected_dependencies


def test_artifact__operation_modules__declare_one_semantic_action() -> None:
    package_root = Path(colored.__file__).parent
    expected_actions = {
        "enablement/identity_derivation.py": {
            "CpnEnablementResultIdentityDeriver"
        },
        "enablement/failure_building.py": {"CpnEnablementFailureBuilder"},
        "enablement/ordering.py": {"CpnEnabledBindingOrderingPolicy"},
        "enablement/transitions.py": {"CpnTransitionEnabler"},
        "firing/occurrence_reconstruction.py": {
            "CpnTokenOccurrenceReconstructor"
        },
        "firing/identity_derivation.py": {"CpnFiringResultIdentityDeriver"},
        "firing/successor_marking.py": {"CpnSuccessorMarkingBuilder"},
        "firing/failure_building.py": {"CpnFiringFailureBuilder"},
        "firing/transitions.py": {"CpnTransitionFirer"},
    }
    for relative_path, expected in expected_actions.items():
        tree = ast.parse(
            (package_root / relative_path).read_text(encoding="utf-8")
        )
        actions = {
            node.name
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and any(
                isinstance(member, ast.FunctionDef) and member.name == "execute"
                for member in node.body
            )
        }
        assert actions == expected
