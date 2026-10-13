"""Mechanical ownership gates for the complete Workflow package."""

import ast
from pathlib import Path

import pytest

_ALLOWED_COMPOUND_MODULES = {
    "petrinet/colored/control/records/type_graph.py",
    "petrinet/colored/enablement/failure_building.py",
    "petrinet/colored/enablement/identity_derivation.py",
    "petrinet/colored/external_outputs.py",
    "petrinet/colored/firing/failure_building.py",
    "petrinet/colored/firing/identity_derivation.py",
    "petrinet/colored/firing/occurrence_reconstruction.py",
    "petrinet/colored/firing/successor_marking.py",
}
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


def test_workflow_package__admits_only_cohesive_compound_module_names(
    pytestconfig: pytest.Config,
) -> None:
    """Every remaining snake-case module is an explicitly reviewed operation."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow"
    compound = {
        str(path.relative_to(package))
        for path in package.rglob("*_*.py")
        if path.name != "__init__.py"
    }
    assert compound == _ALLOWED_COMPOUND_MODULES


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
