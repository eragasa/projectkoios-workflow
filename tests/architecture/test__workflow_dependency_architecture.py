"""Architecture tests for the complete Workflow dependency graph."""

from pathlib import Path

import pytest

from tools.workflow_architecture import (
    WorkflowArchitecturePolicy,
    WorkflowModuleArchitecture,
    dependency_cycles,
    discover_workflow_architecture,
    layer_violations,
    load_workflow_architecture_policy,
)


def _architecture(
    pytestconfig: pytest.Config,
) -> dict[str, WorkflowModuleArchitecture]:
    return discover_workflow_architecture(Path(str(pytestconfig.rootpath)))


def _policy(pytestconfig: pytest.Config) -> WorkflowArchitecturePolicy:
    return load_workflow_architecture_policy(Path(str(pytestconfig.rootpath)))


def _write_module(root: Path, relative: str, source: str = "") -> None:
    destination = root / "src/python/projectkoios/workflow" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source, encoding="utf-8")


def test__workflow_dependencies__form_one_acyclic_layered_graph(
    pytestconfig: pytest.Config,
) -> None:
    """Reject cycles and layer inversions across every production module."""
    architecture = _architecture(pytestconfig)
    policy = _policy(pytestconfig)
    # Purpose: checking one subpackage cannot detect a cycle completed through
    # another layer. The whole distribution must participate in the same graph.
    assert dependency_cycles(architecture) == ()
    # Purpose: acyclicity alone still permits core to depend on runtime or CPN.
    # The human-authored layer policy preserves dependency inversion separately.
    assert (
        layer_violations(
            architecture,
            policy.allowed_layer_dependencies,
        )
        == ()
    )


def test__workflow_dependencies__resolve_every_supported_import_form(
    tmp_path: Path,
) -> None:
    """Exercise import resolution independently of current production syntax."""
    _write_module(tmp_path, "core/__init__.py")
    _write_module(tmp_path, "core/alpha.py", "from . import beta as b\n")
    _write_module(
        tmp_path,
        "core/beta.py",
        "import projectkoios.workflow.core.alpha as a\n",
    )
    _write_module(
        tmp_path,
        "core/consumer.py",
        "from projectkoios.workflow.core import alpha as imported_alpha\n",
    )
    architecture = discover_workflow_architecture(tmp_path)
    # Purpose: fixtures cover relative imports, absolute imports, aliases,
    # package imports, and imported submodules even if production stops using
    # one of those spellings and could no longer act as its own regression case.
    assert architecture["core.alpha"].dependencies == frozenset({"core.beta"})
    assert architecture["core.beta"].dependencies == frozenset({"core.alpha"})
    assert architecture["core.consumer"].dependencies == frozenset(
        {"core.alpha"}
    )
    # Purpose: resolved aliases must feed cycle analysis rather than forming a
    # second, weaker parser path that observes names but misses graph structure.
    assert dependency_cycles(architecture) == (
        ("core.alpha", "core.beta", "core.alpha"),
    )


def test__workflow_dependencies__fixture_detects_layer_inversion(
    tmp_path: Path,
    pytestconfig: pytest.Config,
) -> None:
    """Prove that resolved submodules participate in layer enforcement."""
    _write_module(
        tmp_path, "core/invalid.py", "from ..runtime import adapter\n"
    )
    _write_module(tmp_path, "runtime/adapter.py")
    architecture = discover_workflow_architecture(tmp_path)
    # Purpose: a parser can appear alias-aware yet discard the resolved edge
    # before policy evaluation. This mutation-style fixture must be rejected.
    assert layer_violations(
        architecture,
        _policy(pytestconfig).allowed_layer_dependencies,
    ) == (("core.invalid", "runtime.adapter"),)


def test__workflow_dependencies__composition_roots_are_exact(
    pytestconfig: pytest.Config,
) -> None:
    """Require deliberate dependency sets for every broad assembly root."""
    architecture = _architecture(pytestconfig)
    policy = _policy(pytestconfig)
    roots = policy.composition_root_dependencies
    assert roots.keys() <= architecture.keys()
    for module_name, expected_dependencies in roots.items():
        # Purpose: a fanout threshold alone lets an intended dependency vanish
        # while an unrelated dependency replaces it. Exact policy makes every
        # broad composition edge reviewable and intentional.
        assert architecture[module_name].dependencies == expected_dependencies
        assert (
            len(expected_dependencies) > policy.maximum_ordinary_module_fanout
        )
    for module_name, record in architecture.items():
        if module_name in roots:
            continue
        # Purpose: new high-fanout modules must become explicit reviewed roots,
        # not accidental service locators hidden by import formatting.
        assert (
            len(record.dependencies) <= policy.maximum_ordinary_module_fanout
        ), (
            f"undeclared composition root {module_name}: "
            f"{len(record.dependencies)} dependencies"
        )


def test__workflow_dependencies__prohibit_dynamic_import_aliases(
    pytestconfig: pytest.Config,
    tmp_path: Path,
) -> None:
    """Keep the checked source graph complete and reviewable offline."""
    architecture = _architecture(pytestconfig)
    violations = {
        module_name: record.dynamic_import_lines
        for module_name, record in architecture.items()
        if record.dynamic_import_lines
    }
    # Purpose: dynamic import calls create undeclared edges and could bypass
    # layer, cycle, provider, and effect-boundary checks.
    assert violations == {}

    _write_module(
        tmp_path,
        "runtime/dynamic.py",
        "\n".join(
            (
                "import importlib as loader",
                "from importlib import import_module as load",
                "indirect = loader.import_module",
                "loader.import_module('first')",
                "load('second')",
                "indirect('third')",
                "container = {'load': __import__}['load']",
                "container('fourth')",
                "conditional = eval if True else exec",
                "conditional('fifth')",
                "",
            )
        ),
    )
    fixture = discover_workflow_architecture(tmp_path)["runtime.dynamic"]
    # Purpose: importing or referencing dynamic-execution facilities is itself
    # prohibited, so container, conditional, getattr, or assigned aliases cannot
    # hide authority merely because their eventual call target is indirect.
    assert fixture.dynamic_import_lines == (1, 2, 4, 5, 6, 7, 9)
