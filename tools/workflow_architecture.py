"""Offline Workflow architecture discovery shared by CI and documentation."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

PACKAGE_PREFIX = "projectkoios.workflow"
POLICY_PATH = Path("docs/policies/workflow-architecture-policy.json")
_DYNAMIC_IMPORT_CALLS = frozenset(
    {
        "__import__",
        "builtins.__import__",
        "compile",
        "eval",
        "exec",
        "importlib.import_module",
    }
)
_DYNAMIC_IMPORT_MODULES = frozenset({"builtins", "importlib"})
_DYNAMIC_REFERENCE_NAMES = frozenset(
    {
        "__builtins__",
        "__import__",
        "compile",
        "eval",
        "exec",
        "globals",
        "locals",
    }
)


@dataclass(frozen=True, slots=True)
class WorkflowMethodArchitecture:
    """Static callable-surface facts for one class method."""

    name: str
    positional_parameters: tuple[str, ...]
    parameter_annotations: tuple[str | None, ...]
    return_annotation: str | None
    decorators: frozenset[str]

    @property
    def is_property(self) -> bool:
        """Return whether the method is a property rather than an operation."""
        return "property" in self.decorators


@dataclass(frozen=True, slots=True)
class WorkflowOperationArchitecture:
    """Static ownership and callable-surface facts for one operation class."""

    class_name: str
    methods: tuple[WorkflowMethodArchitecture, ...]
    is_final: bool
    is_slotted: bool

    @property
    def method_names(self) -> frozenset[str]:
        """Return every directly declared method name."""
        return frozenset(method.name for method in self.methods)

    @property
    def public_operation_methods(self) -> frozenset[str]:
        """Return public methods that are not read-only properties."""
        return frozenset(
            method.name
            for method in self.methods
            if not method.name.startswith("_") and not method.is_property
        )

    @property
    def identity_properties(self) -> tuple[WorkflowMethodArchitecture, ...]:
        """Return typed identity properties declared by the operation."""
        return tuple(
            method
            for method in self.methods
            if method.name == "identity" and method.is_property
        )

    @property
    def is_action(self) -> bool:
        """Return whether this class directly declares execute semantics."""
        return "execute" in self.method_names

    @property
    def is_codec_candidate(self) -> bool:
        """Return whether this class claims canonical transport semantics."""
        return self.class_name.endswith("Codec") or bool(
            self.method_names.intersection({"encode", "decode"})
        )


@dataclass(frozen=True, slots=True)
class WorkflowModuleArchitecture:
    """One source module and its statically visible architecture facts."""

    name: str
    path: Path
    dependencies: frozenset[str]
    external_imports: frozenset[str]
    operations: tuple[WorkflowOperationArchitecture, ...]
    nested_class_lines: tuple[int, ...]
    dynamic_import_lines: tuple[int, ...]

    @property
    def action_classes(self) -> tuple[str, ...]:
        """Return every directly declared execute-bearing class."""
        return tuple(
            operation.class_name
            for operation in self.operations
            if operation.is_action
        )

    @property
    def codec_classes(self) -> tuple[str, ...]:
        """Return every class claiming encode/decode codec ownership."""
        return tuple(
            operation.class_name
            for operation in self.operations
            if operation.is_codec_candidate
        )


@dataclass(frozen=True, slots=True)
class WorkflowArchitecturePolicy:
    """Human-authored dependency and effect policy loaded as data."""

    allowed_layer_dependencies: dict[str, frozenset[str]]
    maximum_ordinary_module_fanout: int
    composition_root_dependencies: dict[str, frozenset[str]]
    runtime_internal_dependencies: dict[str, frozenset[str]]
    runtime_external_imports: dict[str, frozenset[str]]


def _string_set_map(value: object, field: str) -> dict[str, frozenset[str]]:
    if type(value) is not dict:
        raise ValueError(f"{field} must be an object")
    result: dict[str, frozenset[str]] = {}
    for key, members in cast(dict[object, object], value).items():
        if type(key) is not str or type(members) is not list:
            raise ValueError(f"{field} must map strings to string arrays")
        if any(type(member) is not str for member in members):
            raise ValueError(f"{field} contains a non-string member")
        result[key] = frozenset(cast(list[str], members))
    return result


def load_workflow_architecture_policy(
    repository_root: Path,
) -> WorkflowArchitecturePolicy:
    """Load the normative human-authored architecture policy document."""
    raw = json.loads(
        (repository_root / POLICY_PATH).read_text(encoding="utf-8")
    )
    if type(raw) is not dict:
        raise ValueError("architecture policy must be an object")
    document = cast(dict[str, object], raw)
    if document.get("schema_version") != 1:
        raise ValueError("unsupported architecture policy schema")
    maximum = document.get("maximum_ordinary_module_fanout")
    if type(maximum) is not int or maximum < 1:
        raise ValueError("maximum_ordinary_module_fanout must be positive")
    return WorkflowArchitecturePolicy(
        allowed_layer_dependencies=_string_set_map(
            document.get("allowed_layer_dependencies"),
            "allowed_layer_dependencies",
        ),
        maximum_ordinary_module_fanout=maximum,
        composition_root_dependencies=_string_set_map(
            document.get("composition_root_dependencies"),
            "composition_root_dependencies",
        ),
        runtime_internal_dependencies=_string_set_map(
            document.get("runtime_internal_dependencies"),
            "runtime_internal_dependencies",
        ),
        runtime_external_imports=_string_set_map(
            document.get("runtime_external_imports"),
            "runtime_external_imports",
        ),
    )


def _module_name(path: Path, package_root: Path) -> str:
    parts = list(path.relative_to(package_root).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _package_parts(module_name: str, path: Path) -> list[str]:
    parts = module_name.split(".") if module_name else []
    return parts if path.name == "__init__.py" else parts[:-1]


def _absolute_import_base(
    node: ast.ImportFrom,
    module_name: str,
    path: Path,
) -> str | None:
    if node.level:
        package = _package_parts(module_name, path)
        ancestor_count = node.level - 1
        if ancestor_count > len(package):
            return None
        parts = package[: len(package) - ancestor_count]
        if node.module:
            parts.extend(node.module.split("."))
        return ".".join(parts)
    if node.module == PACKAGE_PREFIX:
        return ""
    if node.module and node.module.startswith(f"{PACKAGE_PREFIX}."):
        return node.module.removeprefix(f"{PACKAGE_PREFIX}.")
    return None


def _import_targets(
    node: ast.ImportFrom,
    module_name: str,
    path: Path,
    known_modules: frozenset[str],
) -> tuple[set[str], set[str]]:
    base = _absolute_import_base(node, module_name, path)
    if base is None:
        external = set()
        if node.module:
            external.add(node.module)
        return set(), external

    aliases = tuple(alias for alias in node.names if alias.name != "*")
    candidate_by_alias = {
        alias.name: ".".join(part for part in (base, alias.name) if part)
        for alias in aliases
    }
    internal = {
        candidate
        for candidate in candidate_by_alias.values()
        if candidate in known_modules and candidate != module_name
    }
    imports_symbol_from_base = any(
        candidate not in known_modules
        for candidate in candidate_by_alias.values()
    ) or any(alias.name == "*" for alias in node.names)
    if (
        imports_symbol_from_base
        and base in known_modules
        and base != module_name
    ):
        internal.add(base)
    return internal, set()


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _decorator_name(node.value)
        return ".".join(part for part in (parent, node.attr) if part)
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _annotation(node: ast.expr | None) -> str | None:
    return ast.unparse(node) if node is not None else None


def _operation_inventory(
    tree: ast.Module,
) -> tuple[WorkflowOperationArchitecture, ...]:
    operations: list[WorkflowOperationArchitecture] = []
    for class_node in tree.body:
        if not isinstance(class_node, ast.ClassDef):
            continue
        methods = tuple(
            WorkflowMethodArchitecture(
                name=method.name,
                positional_parameters=tuple(
                    argument.arg
                    for argument in (
                        *method.args.posonlyargs,
                        *method.args.args,
                    )
                ),
                parameter_annotations=tuple(
                    _annotation(argument.annotation)
                    for argument in (
                        *method.args.posonlyargs,
                        *method.args.args,
                    )
                ),
                return_annotation=_annotation(method.returns),
                decorators=frozenset(
                    _decorator_name(decorator)
                    for decorator in method.decorator_list
                ),
            )
            for method in class_node.body
            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        names = {method.name for method in methods}
        if not (
            "execute" in names
            or names.intersection({"encode", "decode"})
            or class_node.name.endswith("Codec")
        ):
            continue
        decorators = {
            _decorator_name(decorator)
            for decorator in class_node.decorator_list
        }
        explicit_slots = any(
            isinstance(member, (ast.Assign, ast.AnnAssign))
            and any(
                isinstance(target, ast.Name) and target.id == "__slots__"
                for target in (
                    member.targets
                    if isinstance(member, ast.Assign)
                    else (member.target,)
                )
            )
            for member in class_node.body
        )
        dataclass_slots = any(
            isinstance(decorator, ast.Call)
            and _decorator_name(decorator.func).endswith("dataclass")
            and any(
                keyword.arg == "slots"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in decorator.keywords
            )
            for decorator in class_node.decorator_list
        )
        operations.append(
            WorkflowOperationArchitecture(
                class_name=class_node.name,
                methods=methods,
                is_final=any(
                    decorator.split(".")[-1] == "final"
                    for decorator in decorators
                ),
                is_slotted=explicit_slots or dataclass_slots,
            )
        )
    return tuple(operations)


def _import_bindings(tree: ast.Module) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                bindings[local] = alias.name if alias.asname else local
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "*":
                    continue
                bindings[alias.asname or alias.name] = (
                    f"{node.module}.{alias.name}"
                )
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if value is None:
            continue
        resolved = _resolved_name(value, bindings)
        if resolved not in _DYNAMIC_IMPORT_CALLS:
            continue
        targets = (
            node.targets if isinstance(node, ast.Assign) else (node.target,)
        )
        for target in targets:
            if isinstance(target, ast.Name):
                bindings[target.id] = resolved
    return bindings


def _resolved_name(node: ast.expr, bindings: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return bindings.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        parent = _resolved_name(node.value, bindings)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def discover_workflow_architecture(
    repository_root: Path,
) -> dict[str, WorkflowModuleArchitecture]:
    """Return an alias-aware static graph for every Workflow source module."""
    package_root = repository_root / "src/python/projectkoios/workflow"
    paths = tuple(sorted(package_root.rglob("*.py")))
    path_by_module = {_module_name(path, package_root): path for path in paths}
    known_modules = frozenset(path_by_module)
    result: dict[str, WorkflowModuleArchitecture] = {}

    for module_name, path in path_by_module.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        dependencies: set[str] = set()
        external_imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                internal, external = _import_targets(
                    node,
                    module_name,
                    path,
                    known_modules,
                )
                dependencies.update(internal)
                external_imports.update(external)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == PACKAGE_PREFIX:
                        target = ""
                    elif alias.name.startswith(f"{PACKAGE_PREFIX}."):
                        target = alias.name.removeprefix(f"{PACKAGE_PREFIX}.")
                    else:
                        external_imports.add(alias.name)
                        continue
                    if target in known_modules and target != module_name:
                        dependencies.add(target)

        top_level_class_ids = {
            id(node) for node in tree.body if isinstance(node, ast.ClassDef)
        }
        nested_class_lines = tuple(
            sorted(
                node.lineno
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
                and id(node) not in top_level_class_ids
            )
        )
        bindings = _import_bindings(tree)
        dynamic_import_line_set: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                alias.name.split(".", 1)[0] in _DYNAMIC_IMPORT_MODULES
                for alias in node.names
            ):
                dynamic_import_line_set.add(node.lineno)
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.split(".", 1)[0] in _DYNAMIC_IMPORT_MODULES
            ):
                dynamic_import_line_set.add(node.lineno)
            elif (
                isinstance(node, ast.Name)
                and node.id in _DYNAMIC_REFERENCE_NAMES
            ):
                dynamic_import_line_set.add(node.lineno)
            elif (
                isinstance(node, ast.Call)
                and _resolved_name(node.func, bindings) in _DYNAMIC_IMPORT_CALLS
            ):
                dynamic_import_line_set.add(node.lineno)
        dynamic_import_lines = tuple(sorted(dynamic_import_line_set))
        result[module_name] = WorkflowModuleArchitecture(
            name=module_name,
            path=path,
            dependencies=frozenset(dependencies),
            external_imports=frozenset(external_imports),
            operations=_operation_inventory(tree),
            nested_class_lines=nested_class_lines,
            dynamic_import_lines=dynamic_import_lines,
        )
    return result


def dependency_cycles(
    architecture: dict[str, WorkflowModuleArchitecture],
) -> tuple[tuple[str, ...], ...]:
    """Return deterministic module cycles from the complete internal graph."""
    visited: set[str] = set()
    active: list[str] = []
    cycles: set[tuple[str, ...]] = set()

    def visit(module_name: str) -> None:
        if module_name in active:
            start = active.index(module_name)
            cycle = tuple(active[start:] + [module_name])
            rotations = tuple(
                cycle[index:-1] + cycle[:index] + (cycle[index],)
                for index in range(len(cycle) - 1)
            )
            cycles.add(min(rotations))
            return
        if module_name in visited:
            return
        active.append(module_name)
        for dependency in sorted(architecture[module_name].dependencies):
            visit(dependency)
        active.pop()
        visited.add(module_name)

    for module_name in sorted(architecture):
        visit(module_name)
    return tuple(sorted(cycles))


def layer_violations(
    architecture: dict[str, WorkflowModuleArchitecture],
    allowed_layer_dependencies: dict[str, frozenset[str]],
) -> tuple[tuple[str, str], ...]:
    """Return internal edges that violate human-authored layer policy."""
    violations: list[tuple[str, str]] = []
    for module_name, record in architecture.items():
        source_layer = module_name.split(".", 1)[0] if module_name else ""
        allowed = allowed_layer_dependencies.get(source_layer, frozenset())
        for dependency in record.dependencies:
            target_layer = dependency.split(".", 1)[0] if dependency else ""
            if target_layer not in allowed:
                violations.append((module_name, dependency))
    return tuple(sorted(violations))
