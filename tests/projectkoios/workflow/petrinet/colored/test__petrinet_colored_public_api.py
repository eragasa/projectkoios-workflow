r"""Software verification of petrinet.colored public value surface.

Evidence profile: routine

Bounded artifact scope: package exports and dependency direction for the implemented
Architecture v2 value/token and marking/binding slices.

Facet and represented meaning

The artifact is the supported full-name ``projectkoios.workflow.petrinet.colored`` import
surface and its inward generic dependency boundary.

Intrinsic and cross-object scope

Exact exports and the prohibition on imports from Project Koios core, runtime,
adapter, application, or research-domain owners are covered. Class-local invariants
are owned by class tests.

VVUQ and scientific exclusions

These structural checks establish software ownership only. They establish no
numerical verification, scientific validation, uncertainty quantification,
calculation execution, or human acceptance.
"""

from __future__ import annotations

import ast
from itertools import chain
from pathlib import Path

import pytest

import projectkoios.workflow.petrinet.colored as colored

pytestmark = pytest.mark.software_verification


def collect_import_names(package_root: Path) -> set[str]:
    """Evidence ID: Owns no identifier; supports dependency evidence in this module.

    Requirement: Dependency evidence needs every syntactic import in the bounded
    package modules.

    Acceptance: The helper returns absolute modules and imported parent members for
    every parsed import statement.
    """
    trees = []
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        trees.append(ast.walk(tree))
    nodes = tuple(chain.from_iterable(trees))
    direct = {
        alias.name
        for node in nodes
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    from_modules = {
        node.module
        for node in nodes
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    from_members = {
        f"{node.module}.{alias.name}"
        for node in nodes
        if isinstance(node, ast.ImportFrom) and node.module is not None
        for alias in node.names
    }
    relative_members = {
        alias.name
        for node in nodes
        if isinstance(node, ast.ImportFrom) and node.level > 0
        for alias in node.names
    }
    return direct | from_modules | from_members | relative_members


def test_public_api__package_initializer__is_not_an_object_facade() -> None:
    """The package boundary does not aggregate semantic owner objects."""
    assert colored.__all__ == ()


def test_public_import_inventory__names_every_semantic_owner_module(
    pytestconfig: pytest.Config,
) -> None:
    repository_root = pytestconfig.rootpath
    package_root = Path(colored.__file__).parent
    inventory = (
        repository_root / "docs/contracts/workflow-cpn-public-imports.md"
    ).read_text(encoding="utf-8")
    prefix = "projectkoios.workflow.petrinet.colored"
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


def test_production_operations__forbid_hidden_callable_semantics() -> None:
    package_root = Path(colored.__file__).parent
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


def test_production_actions__use_one_typed_request_and_one_response() -> None:
    package_root = Path(colored.__file__).parent
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for class_node in (
            node for node in tree.body if isinstance(node, ast.ClassDef)
        ):
            methods = tuple(
                node
                for node in class_node.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            execute_methods = tuple(
                node for node in methods if node.name == "execute"
            )
            if not execute_methods:
                continue
            assert len(execute_methods) == 1
            explicit_slots = any(
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "__slots__"
                    for target in node.targets
                )
                for node in class_node.body
            )
            dataclass_slots = any(
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "dataclass"
                and any(
                    keyword.arg == "slots"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in decorator.keywords
                )
                for decorator in class_node.decorator_list
            )
            assert explicit_slots or dataclass_slots, (
                f"{path}:{class_node.lineno} action must be slotted"
            )
            execute = execute_methods[0]
            assert len(execute.args.args) == 2, (
                f"{path}:{execute.lineno} must accept self and one request"
            )
            request = execute.args.args[1]
            assert request.annotation is not None
            request_type = ast.unparse(request.annotation)
            assert request_type.endswith(("Input", "Request")), (
                f"{path}:{execute.lineno} has unowned request {request_type}"
            )
            assert execute.returns is not None
            response_type = ast.unparse(execute.returns)
            assert response_type.startswith(("Cpn", "Workflow")), (
                f"{path}:{execute.lineno} has non-domain response {response_type}"
            )
            identity_members = tuple(
                node
                for node in class_node.body
                if isinstance(node, ast.FunctionDef)
                and node.name == "identity"
                and any(
                    isinstance(decorator, ast.Name)
                    and decorator.id == "property"
                    for decorator in node.decorator_list
                )
            )
            assert len(identity_members) == 1, (
                f"{path}:{class_node.lineno} action lacks one typed identity property"
            )
            assert identity_members[0].returns is not None
            public_semantic_methods = {
                node.name
                for node in methods
                if not node.name.startswith("_")
                and not any(
                    isinstance(decorator, ast.Name)
                    and decorator.id == "property"
                    for decorator in node.decorator_list
                )
            }
            assert public_semantic_methods == {"execute"}, (
                f"{path}:{class_node.lineno} action exposes multiple operations: "
                f"{sorted(public_semantic_methods)}"
            )


def test_canonical_codecs__only_transform_immutable_transport_objects() -> None:
    package_root = Path(colored.__file__).parent
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for class_node in (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name.endswith("Codec")
        ):
            slots = tuple(
                node
                for node in class_node.body
                if isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "__slots__"
                    for target in node.targets
                )
            )
            assert len(slots) == 1, (
                f"{path}:{class_node.lineno} codec must define __slots__"
            )
            identity_members = tuple(
                node
                for node in class_node.body
                if isinstance(node, ast.FunctionDef)
                and node.name == "identity"
                and any(
                    isinstance(decorator, ast.Name)
                    and decorator.id == "property"
                    for decorator in node.decorator_list
                )
            )
            assert len(identity_members) == 1
            assert identity_members[0].returns is not None
            methods = {
                node.name
                for node in class_node.body
                if isinstance(node, ast.FunctionDef)
                and not node.name.startswith("_")
                and not any(
                    isinstance(decorator, ast.Name)
                    and decorator.id == "property"
                    for decorator in node.decorator_list
                )
            }
            assert methods == {"encode", "decode"}, (
                f"{path}:{class_node.lineno} codec exposes non-transport operations"
            )
            for node in class_node.body:
                if (
                    not isinstance(node, ast.FunctionDef)
                    or node.name not in methods
                ):
                    continue
                assert len(node.args.args) == 2
                request = node.args.args[1]
                assert request.annotation is not None
                assert ast.unparse(request.annotation).endswith("Input")
                assert node.returns is not None


def test_production_data__contains_no_unresolved_executable_dependencies() -> (
    None
):
    package_root = Path(colored.__file__).parent
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
                        f"{path}:{class_node.lineno} dataclass omits {option}=True"
                    )
                    value = options[option]
                    assert (
                        isinstance(value, ast.Constant) and value.value is True
                    ), (
                        f"{path}:{class_node.lineno} dataclass must set {option}=True"
                    )
            for node in class_node.body:
                if not isinstance(node, ast.AnnAssign):
                    continue
                annotation = ast.unparse(node.annotation)
                assert annotation != "object", (
                    f"{path}:{node.lineno} data field has unspecified object state"
                )
                assert not annotation.startswith(("list[", "dict[")), (
                    f"{path}:{node.lineno} data field exposes mutable collection state"
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
                        f"{path}:{node.lineno} data bag contains executable behavior"
                    )


def test_artifact__static_surface__forbids_any_and_legacy_aliases() -> None:
    """The owner kernel has neither dynamic Any nor legacy nominal aliases."""
    package_root = Path(colored.__file__).parent
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


def test_artifact__dependency__excludes_domain_imports() -> None:
    """Evidence ID: SV-PETRINET-018

    Requirement: The generic package must not depend on Project Koios core,
    runtime, adapters, applications, or research-domain owners.

    Acceptance: No absolute or relative import in the implemented package resolves
    to a prohibited package prefix.
    """
    package_root = Path(colored.__file__).parent
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
    imported = collect_import_names(package_root)
    assert not any(name.startswith(prohibited) for name in imported)
