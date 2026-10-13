"""Mechanical ownership gates for the complete Workflow package."""

import ast
from pathlib import Path

import pytest

_PROHIBITED_BUCKET_NAMES = {
    "models.py",
    "records.py",
    "service.py",
    "store.py",
    "workflow.py",
}


def test_workflow_package__has_no_compound_package_directories(
    pytestconfig: pytest.Config,
) -> None:
    """Compound ownership is represented by nested namespaces, not suffixes."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow"
    compound = tuple(
        sorted(
            str(path.relative_to(package))
            for path in package.rglob("*")
            if path.is_dir() and path.name != "__pycache__" and "_" in path.name
        )
    )
    assert compound == ()


def test_workflow_package__has_no_compound_module_names(
    pytestconfig: pytest.Config,
) -> None:
    """Compound semantic ownership is represented by nested namespaces."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow"
    compound = {
        str(path.relative_to(package))
        for path in package.rglob("*_*.py")
        if path.name != "__init__.py"
    }
    assert compound == set()


def test_workflow_package__has_no_import_facades_or_import_dominated_modules(
    pytestconfig: pytest.Config,
) -> None:
    """Require concrete ownership and bounded import declarations."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow"
    for path in package.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        source = path.read_text(encoding="utf-8")
        module = ast.parse(source)
        statements = tuple(
            node
            for node in module.body
            if not (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and type(node.value.value) is str
            )
        )
        imports = tuple(
            node
            for node in statements
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )
        owned_statements = tuple(
            node
            for node in statements
            if not isinstance(node, (ast.Import, ast.ImportFrom))
        )
        assert owned_statements, f"import facade: {path.relative_to(package)}"
        import_lines = sum(
            (node.end_lineno or node.lineno) - node.lineno + 1
            for node in imports
            if not (
                isinstance(node, ast.ImportFrom) and node.module == "__future__"
            )
        )
        assert import_lines * 4 <= len(source.splitlines()), (
            f"import-dominated module: {path.relative_to(package)} "
            f"({import_lines}/{len(source.splitlines())} lines)"
        )


def test_workflow_package__contains_no_generic_bucket_modules(
    pytestconfig: pytest.Config,
) -> None:
    """Keep broad generic bucket modules absent."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow"
    buckets = tuple(
        sorted(
            str(path.relative_to(package))
            for path in package.rglob("*.py")
            if path.name in _PROHIBITED_BUCKET_NAMES
        )
    )
    assert buckets == ()


def test_workflow_package__keeps_every_initializer_as_an_empty_boundary(
    pytestconfig: pytest.Config,
) -> None:
    """Initializers contain exactly a docstring and annotated empty __all__."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow"
    for initializer in package.rglob("__init__.py"):
        module = ast.parse(initializer.read_text())
        assert len(module.body) == 2, initializer
        assert isinstance(module.body[0], ast.Expr), initializer
        assert isinstance(module.body[0].value, ast.Constant), initializer
        assignment = module.body[1]
        assert isinstance(assignment, ast.AnnAssign), initializer
        assert isinstance(assignment.target, ast.Name), initializer
        assert assignment.target.id == "__all__", initializer
        assert isinstance(assignment.value, ast.Tuple), initializer
        assert assignment.value.elts == [], initializer
