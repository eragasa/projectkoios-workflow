"""Ownership gates for cohesive review workflow namespaces."""

import ast
from pathlib import Path

import pytest


def test_review_packages__use_review_namespace_without_suffix_siblings(
    pytestconfig: pytest.Config,
) -> None:
    """Keep review kinds below review, never as top-level suffix packages."""
    root = Path(str(pytestconfig.rootpath))
    workflow = root / "src/python/projectkoios/workflow"
    suffix_packages = tuple(
        path
        for path in workflow.iterdir()
        if path.is_dir() and path.name.endswith("_review")
    )
    assert suffix_packages == ()
    assert (workflow / "review/course/execution.py").is_file()
    assert (workflow / "review/reference/execution.py").is_file()


def test_review_packages__keep_initializers_as_empty_boundaries(
    pytestconfig: pytest.Config,
) -> None:
    """Review namespace initializers contain no facade imports or exports."""
    root = Path(str(pytestconfig.rootpath))
    review = root / "src/python/projectkoios/workflow/review"
    for initializer in (
        review / "__init__.py",
        review / "course/__init__.py",
        review / "reference/__init__.py",
    ):
        module = ast.parse(initializer.read_text())
        assert len(module.body) == 2
        assert isinstance(module.body[0], ast.Expr)
        assert isinstance(module.body[0].value, ast.Constant)
        assignment = module.body[1]
        assert isinstance(assignment, ast.AnnAssign)
        assert isinstance(assignment.target, ast.Name)
        assert assignment.target.id == "__all__"
        assert isinstance(assignment.value, ast.Tuple)
        assert assignment.value.elts == []
