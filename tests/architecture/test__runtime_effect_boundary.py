"""Architecture tests for the effect-free runtime coordinator."""

from dataclasses import replace
from pathlib import Path

import pytest

from tools.workflow_architecture import (
    WorkflowArchitecturePolicy,
    WorkflowModuleArchitecture,
    discover_workflow_architecture,
    load_workflow_architecture_policy,
)


def _runtime_records(
    architecture: dict[str, WorkflowModuleArchitecture],
) -> dict[str, WorkflowModuleArchitecture]:
    return {
        module_name: record
        for module_name, record in architecture.items()
        if module_name == "runtime" or module_name.startswith("runtime.")
    }


def _runtime_policy_mismatches(
    runtime_records: dict[str, WorkflowModuleArchitecture],
    policy: WorkflowArchitecturePolicy,
) -> dict[str, tuple[frozenset[str], frozenset[str]]]:
    mismatches: dict[str, tuple[frozenset[str], frozenset[str]]] = {}
    expected_modules = set(policy.runtime_internal_dependencies)
    expected_modules.update(policy.runtime_external_imports)
    for module_name in sorted(set(runtime_records) | expected_modules):
        record = runtime_records.get(module_name)
        actual_internal = (
            record.dependencies if record is not None else frozenset()
        )
        actual_external = (
            record.external_imports if record is not None else frozenset()
        )
        expected_internal = policy.runtime_internal_dependencies.get(
            module_name,
            frozenset(),
        )
        expected_external = policy.runtime_external_imports.get(
            module_name,
            frozenset(),
        )
        if (
            record is None
            or actual_internal != expected_internal
            or actual_external != expected_external
        ):
            mismatches[module_name] = (actual_internal, actual_external)
    return mismatches


def test__runtime_boundary__recursively_covers_exact_runtime_modules(
    pytestconfig: pytest.Config,
) -> None:
    """Prove that runtime boundary evidence scans every nested module."""
    root = Path(str(pytestconfig.rootpath))
    architecture = discover_workflow_architecture(root)
    policy = load_workflow_architecture_policy(root)
    runtime_records = _runtime_records(architecture)
    expected_modules = set(policy.runtime_internal_dependencies)
    # Purpose: an exact recursive inventory fails when a subpackage is skipped,
    # deleted, or added without an explicit policy decision. A nonempty witness
    # count alone cannot prove that every effect-bearing module was examined.
    assert set(runtime_records) == expected_modules
    assert expected_modules == set(policy.runtime_external_imports)
    assert any(module_name.count(".") >= 2 for module_name in runtime_records)


def test__runtime_boundary__admits_only_declared_ports_and_dependencies(
    pytestconfig: pytest.Config,
) -> None:
    """Keep all runtime dependencies behind explicitly reviewed boundaries."""
    root = Path(str(pytestconfig.rootpath))
    runtime_records = _runtime_records(discover_workflow_architecture(root))
    policy = load_workflow_architecture_policy(root)
    # Purpose: exact positive policy rejects every undeclared persistence,
    # provider, CPN, network, process, clock, randomness, or plugin dependency
    # regardless of package spelling; a short denylist cannot do that.
    assert _runtime_policy_mismatches(runtime_records, policy) == {}


def test__runtime_boundary__mutation_witnesses_catch_alternative_effects(
    pytestconfig: pytest.Config,
) -> None:
    """Demonstrate that representative renamed effect packages cannot pass."""
    root = Path(str(pytestconfig.rootpath))
    records = _runtime_records(discover_workflow_architecture(root))
    policy = load_workflow_architecture_policy(root)
    target_name = "runtime.execution.local"
    target = records[target_name]
    for external_effect in ("sqlite3", "pm4py", "urllib.request"):
        mutated = dict(records)
        mutated[target_name] = replace(
            target,
            external_imports=target.external_imports | {external_effect},
        )
        # Purpose: category examples prove that enforcement is based on a
        # positive contract, not merely today's prohibited library names.
        assert target_name in _runtime_policy_mismatches(mutated, policy)
    mutated = dict(records)
    mutated[target_name] = replace(
        target,
        dependencies=target.dependencies | {"persistence.revisions.postgresql"},
    )
    # Purpose: a newly named concrete internal adapter must also require an
    # explicit policy change rather than bypassing an exact SQLite comparison.
    assert target_name in _runtime_policy_mismatches(mutated, policy)
