r"""Software verification of petrinet.colored public value surface.

Evidence profile: routine

Bounded artifact scope: package exports and dependency direction for the
implemented Architecture v2 value/token and marking/binding slices.

Facet and represented meaning

The artifact is the supported full-name
``projectkoios.workflow.petrinet.colored`` import surface and its inward generic
dependency boundary.

Intrinsic and cross-object scope

Exact exports and the prohibition on imports from Project Koios core, runtime,
adapter, application, or research-domain owners are covered. Class-local
invariants are owned by class tests.

VVUQ and scientific exclusions

These structural checks establish software ownership only. They establish no
numerical verification, scientific validation, uncertainty quantification,
calculation execution, or human acceptance.
"""

from __future__ import annotations

import ast
from itertools import chain
from pathlib import Path

import projectkoios.workflow.petrinet.colored as colored
import pytest

from tools.workflow_architecture import discover_workflow_architecture

pytestmark = pytest.mark.software_verification


def test_public_import_inventory__names_every_semantic_owner_module(
    pytestconfig: pytest.Config,
) -> None:
    repository_root = pytestconfig.rootpath
    package_root = Path(colored.__file__).parent
    inventory = (
        repository_root / "docs/contracts/workflow-cpn-public-imports.md"
    ).read_text(encoding="utf-8")
    prefix = "projectkoios.workflow.petrinet.colored"
    # Purpose: direct semantic-owner imports are usable only when every owner is
    # present in the checked human/LLM discovery inventory.
    for path in package_root.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if not any(
            isinstance(node, ast.ClassDef)
            and node.name.startswith(("Cpn", "Workflow"))
            for node in tree.body
        ):
            continue
        suffix = ".".join(path.relative_to(package_root).with_suffix("").parts)
        assert f"`{prefix}.{suffix}`" in inventory


def test_mirrored_class_evidence__is_not_name_only(
    pytestconfig: pytest.Config,
) -> None:
    test_root = (
        pytestconfig.rootpath / "tests/projectkoios/workflow/petrinet/colored"
    )
    # Purpose: a same-named test file is not evidence unless it exercises a
    # behavioral or structural invariant of the mirrored public type.
    for path in test_root.glob("test__*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        has_behavioral_or_structural_assertion = any(
            isinstance(node, ast.With)
            or (
                isinstance(node, ast.Assert)
                and not any(
                    isinstance(member, ast.Attribute)
                    and member.attr == "__name__"
                    for member in ast.walk(node)
                )
            )
            for node in ast.walk(tree)
        )
        assert has_behavioral_or_structural_assertion, (
            f"mirrored class evidence is name-only: {path}"
        )


def test_production_operations__forbid_hidden_callable_semantics() -> None:
    package_root = Path(colored.__file__).parent
    # Purpose: callbacks, private methods, lambdas, and module-level functions
    # would hide executable semantics from the operation and identity inventory.
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_functions = tuple(
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        assert not module_functions, (
            f"{path} declares module-level semantic functions: "
            f"{[item.name for item in module_functions]}"
        )
        assert not any(
            isinstance(node, ast.Lambda) for node in ast.walk(tree)
        ), f"{path} declares anonymous callable semantics"
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            is_dunder = node.name.startswith("__") and node.name.endswith("__")
            assert node.name != "__call__", (
                f"{path}:{node.lineno} declares semantic __call__"
            )
            assert is_dunder or not node.name.startswith("_"), (
                f"{path}:{node.lineno} declares private callable {node.name}"
            )
            decorator_names = {
                decorator.id
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Name)
            }
            assert not decorator_names.intersection(
                {"staticmethod", "classmethod"}
            ), f"{path}:{node.lineno} declares static/class callable semantics"


def test_production_data__contains_no_unresolved_executable_dependencies() -> (
    None
):
    package_root = Path(colored.__file__).parent
    # Purpose: immutable records may describe configuration and results but must
    # not smuggle actions, callbacks, mutable containers, or unspecified state.
    action_names: set[str] = set()
    trees: list[tuple[Path, ast.Module]] = []
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        trees.append((path, tree))
        for class_node in (
            node for node in tree.body if isinstance(node, ast.ClassDef)
        ):
            if any(
                isinstance(node, ast.FunctionDef) and node.name == "execute"
                for node in class_node.body
            ):
                action_names.add(class_node.name)
    for path, tree in trees:
        for class_node in (
            node for node in tree.body if isinstance(node, ast.ClassDef)
        ):
            dataclass_decorators = tuple(
                decorator
                for decorator in class_node.decorator_list
                if isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "dataclass"
            )
            declared_fields = tuple(
                node
                for node in class_node.body
                if isinstance(node, ast.AnnAssign)
            )
            has_execute = any(
                isinstance(node, ast.FunctionDef) and node.name == "execute"
                for node in class_node.body
            )
            if declared_fields and not has_execute:
                assert dataclass_decorators, (
                    f"{path}:{class_node.lineno} data class must be a dataclass"
                )
            for decorator in dataclass_decorators:
                options = {
                    keyword.arg: keyword.value for keyword in decorator.keywords
                }
                for option in ("frozen", "slots"):
                    assert option in options, (
                        f"{path}:{class_node.lineno} dataclass omits "
                        f"{option}=True"
                    )
                    value = options[option]
                    assert (
                        isinstance(value, ast.Constant) and value.value is True
                    ), (
                        f"{path}:{class_node.lineno} dataclass must set "
                        f"{option}=True"
                    )
            for node in class_node.body:
                if not isinstance(node, ast.AnnAssign):
                    continue
                annotation = ast.unparse(node.annotation)
                assert annotation != "object", (
                    f"{path}:{node.lineno} data field has unspecified "
                    "object state"
                )
                assert not annotation.startswith(("list[", "dict[")), (
                    f"{path}:{node.lineno} data field exposes mutable "
                    "collection state"
                )
                assert "Callable" not in annotation
                executable_fields = action_names.intersection(
                    part
                    for part in annotation.replace("[", " ")
                    .replace("]", " ")
                    .replace("|", " ")
                    .split()
                )
                if executable_fields:
                    assert class_node.name.endswith(("Response", "Result")), (
                        f"{path}:{node.lineno} data bag contains executable "
                        "behavior"
                    )


def test_artifact__static_surface__forbids_any_and_legacy_aliases() -> None:
    """The owner kernel has neither dynamic Any nor legacy nominal aliases."""
    package_root = Path(colored.__file__).parent
    # Purpose: one precise Cpn*/Workflow* vocabulary keeps request boundaries
    # statically checkable and prevents compatibility aliases becoming facades.
    paths = tuple(package_root.rglob("*.py"))
    nodes = tuple(
        chain.from_iterable(
            ast.walk(ast.parse(path.read_text(encoding="utf-8")))
            for path in paths
        )
    )
    imported_any = {
        alias.name
        for node in nodes
        if isinstance(node, ast.ImportFrom) and node.module == "typing"
        for alias in node.names
        if alias.name == "Any"
    }
    legacy_classes = {
        node.name
        for node in nodes
        if isinstance(node, ast.ClassDef)
        and node.name.startswith("ColoredPetriNet")
    }
    legacy_assignments = {
        target.id
        for node in nodes
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (
            node.targets if isinstance(node, ast.Assign) else (node.target,)
        )
        if isinstance(target, ast.Name)
        and target.id.startswith("ColoredPetriNet")
    }
    assert imported_any == set()
    assert legacy_classes == set()
    assert legacy_assignments == set()
    assert all("ColoredPetriNet" not in path.name for path in paths)


def test_artifact__dependency__excludes_domain_imports(
    pytestconfig: pytest.Config,
) -> None:
    """Evidence ID: SV-PETRINET-018

    Requirement: The generic package must not depend on Project Koios core,
    runtime, adapters, applications, or research-domain owners.

    Acceptance: No absolute or relative import in the implemented package
    resolves to a prohibited package prefix.
    """
    architecture = discover_workflow_architecture(
        Path(str(pytestconfig.rootpath))
    )
    prohibited = (
        "projectkoios",
        "core",
        "runtime",
        "adapters",
        "api",
        "courses",
        "ingestion",
        "obsidian",
        "references",
        "research",
        "search",
    )
    imported = {
        imported_name
        for module_name, record in architecture.items()
        if module_name.startswith("petrinet.colored")
        for imported_name in record.external_imports
    }
    # Purpose: the generic CPN SDK cannot acquire product, runtime, adapter, or
    # scientific authority through imports outside the one shared graph.
    assert not any(name.startswith(prohibited) for name in imported)
