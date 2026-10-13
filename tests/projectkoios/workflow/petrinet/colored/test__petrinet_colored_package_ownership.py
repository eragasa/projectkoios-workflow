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
        "control/records/types/graph.py",
        "shadow/firing.py",
        "shadow/replay/action.py",
        "validation/definitions.py",
        "validation/markings.py",
    } <= relative_paths
    assert (
        not {
            "canonical.py",
            "canonical/firing_contracts.py",
            "canonical/firings.py",
            "canonical_definition.py",
            "canonical_expressions.py",
            "canonical_marking.py",
            "control_records.py",
            "enablement.py",
            "enablement/outcomes.py",
            "expression_operations.py",
            "expressions.py",
            "firing.py",
            "firing/outcomes.py",
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
        "enablement.results.definition": set(),
        "enablement.results.identity": {"enablement.results.definition"},
        "enablement.failures.building": {
            "enablement.results.definition",
            "enablement.results.identity",
        },
        "enablement.ordering": {"enablement.results.definition"},
        "enablement.transitions": {
            "enablement.failures.building",
            "enablement.ordering",
            "enablement.results.definition",
            "enablement.results.identity",
        },
        "firing.inputs": {"enablement.results.definition"},
        "firing.audits": set(),
        "firing.results.definition": {"firing.audits", "firing.inputs"},
        "firing.occurrences.reconstruction": {"firing.audits"},
        "firing.results.identity": {
            "firing.audits",
            "firing.inputs",
            "firing.results.definition",
        },
        "firing.markings.successor": {"firing.audits", "firing.inputs"},
        "firing.failures.building": {
            "firing.inputs",
            "firing.results.definition",
            "firing.results.identity",
        },
        "firing.transitions": {
            "enablement.transitions",
            "firing.audits",
            "firing.failures.building",
            "firing.inputs",
            "firing.markings.successor",
            "firing.occurrences.reconstruction",
            "firing.results.definition",
            "firing.results.identity",
        },
        "canonical.firing.results.identity": set(),
        "canonical.firing.results.documents": {"firing.results.definition"},
        "canonical.firing.results.codec": {
            "canonical.firing.results.documents",
            "canonical.firing.results.identity",
            "firing.inputs",
            "firing.results.definition",
        },
        "payloads.references.definition": set(),
        "payloads.references.canonical": {"payloads.references.definition"},
        "payloads.references.assembly": {"payloads.references.definition"},
        "payloads.references.verification": {"payloads.references.definition"},
    }
    for (
        module_name,
        expected_dependencies,
    ) in expected_operation_dependencies.items():
        actual_dependencies = {
            dependency
            for dependency in dependencies[module_name]
            if dependency.startswith(
                (
                    "canonical.firing.results.",
                    "enablement.",
                    "firing.",
                    "payloads.references.",
                )
            )
        }
        assert actual_dependencies == expected_dependencies


def test_artifact__operation_modules__declare_one_semantic_action() -> None:
    package_root = Path(colored.__file__).parent
    expected_actions = {
        "control/records/types/graph.py": {
            "CpnControlRecordTypeGraphValidator"
        },
        "enablement/results/identity.py": {
            "CpnEnablementResultIdentityDeriver"
        },
        "enablement/failures/building.py": {"CpnEnablementFailureBuilder"},
        "enablement/ordering.py": {"CpnEnabledBindingOrderingPolicy"},
        "enablement/transitions.py": {"CpnTransitionEnabler"},
        "outputs/external.py": {"CpnExternalOutputValidator"},
        "firing/occurrences/reconstruction.py": {
            "CpnTokenOccurrenceReconstructor"
        },
        "firing/results/identity.py": {"CpnFiringResultIdentityDeriver"},
        "firing/markings/successor.py": {"CpnSuccessorMarkingBuilder"},
        "firing/failures/building.py": {"CpnFiringFailureBuilder"},
        "firing/transitions.py": {"CpnTransitionFirer"},
        "payloads/references/assembly.py": {
            "WorkflowDomainPayloadReferenceAssembler"
        },
        "payloads/references/verification.py": {
            "WorkflowDomainPayloadReferenceVerifier"
        },
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
