"""Mechanical ownership gates for the complete Workflow package."""

import ast
from pathlib import Path

import pytest

_PROHIBITED_CPN_SHIMS = {
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
    # Purpose: suffix-based directories obscure which noun owns the contract;
    # nested namespaces keep ownership navigable and mechanically comparable.
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
    # Purpose: a compound filename often smuggles two owner concepts back into
    # one module after their package boundary was deliberately separated.
    assert compound == set()


def test_workflow_package__has_no_import_facades(
    pytestconfig: pytest.Config,
) -> None:
    """Require every concrete module to own more than imported names."""
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
        owned_statements = tuple(
            node
            for node in statements
            if not isinstance(node, (ast.Import, ast.ImportFrom))
        )
        # Purpose: aggregate import facades create an accidental second public
        # API and hide the module that actually owns behavior or representation.
        assert owned_statements, f"import facade: {path.relative_to(package)}"


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
    # Purpose: generic buckets accumulate unrelated owners while preserving a
    # superficially tidy filename, defeating change locality and review scope.
    assert buckets == ()


def test_workflow_package__contains_no_retired_cpn_shims(
    pytestconfig: pytest.Config,
) -> None:
    """Prevent retired aggregate CPN paths from becoming compatibility APIs."""
    root = Path(str(pytestconfig.rootpath))
    package = root / "src/python/projectkoios/workflow/petrinet/colored"
    present = {path.name for path in package.glob("*.py")}
    # Purpose: an obsolete shim would bypass direct semantic-owner imports and
    # make removal impossible once a provider accidentally depends on it.
    assert not (present & _PROHIBITED_CPN_SHIMS)


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
        # Purpose: initializers identify namespaces only; registrations and
        # re-exports would create hidden discovery and aggregate compatibility.
        assert assignment.value.elts == [], initializer
