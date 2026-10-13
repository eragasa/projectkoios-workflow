"""Architecture tests for complete CPN semantic-operation ownership."""

import json
from pathlib import Path

import pytest

from tools.workflow_architecture import (
    WorkflowMethodArchitecture,
    WorkflowOperationArchitecture,
    discover_workflow_architecture,
)


def _method(
    operation: WorkflowOperationArchitecture,
    name: str,
) -> WorkflowMethodArchitecture:
    return next(method for method in operation.methods if method.name == name)


def test__semantic_operation__has_one_complete_owner_module(
    pytestconfig: pytest.Config,
) -> None:
    """Bind each independently callable CPN operation to one typed owner."""
    architecture = discover_workflow_architecture(
        Path(str(pytestconfig.rootpath))
    )
    for module_name, record in architecture.items():
        if not module_name.startswith("petrinet.colored"):
            continue
        # Purpose: nested operation classes have no stable importable owner;
        # they escape module SDK discovery and identity uniqueness checks.
        assert record.nested_class_lines == (), (
            f"nested classes in {module_name}: {record.nested_class_lines}"
        )
        # Purpose: two execute-bearing classes are independently replaceable
        # semantics. Sharing a module would recreate broad operation buckets.
        assert len(record.action_classes) <= 1, (
            f"multiple semantic actions in {module_name}: "
            f"{record.action_classes}"
        )
        # Purpose: a codec is the sole paired operation and cannot share its
        # owner module with an execute action or another transport contract.
        assert not (record.action_classes and record.codec_classes), (
            f"action and codec ownership mixed in {module_name}"
        )
        assert len(record.codec_classes) <= 1, (
            f"multiple canonical codecs in {module_name}: "
            f"{record.codec_classes}"
        )

        for operation in record.operations:
            if operation.is_action:
                expected_methods = frozenset({"execute"})
                method_names = ("execute",)
            elif operation.is_codec_candidate:
                expected_methods = frozenset({"encode", "decode"})
                method_names = ("encode", "decode")
            else:
                continue
            # Purpose: additional public callable methods would create hidden
            # independently invocable semantics inside an apparently single
            # operation owner.
            assert operation.public_operation_methods == expected_methods, (
                f"unexpected operation surface in {module_name}."
                f"{operation.class_name}: "
                f"{sorted(operation.public_operation_methods)}"
            )
            # Purpose: operation objects are closed values whose implementation
            # cannot be subclassed or extended with unretained mutable state.
            assert operation.is_final
            assert operation.is_slotted
            assert len(operation.identity_properties) == 1
            assert operation.identity_properties[0].return_annotation
            for method_name in method_names:
                method = _method(operation, method_name)
                # Purpose: every operation crosses one immutable typed request
                # boundary and returns one explicit typed response boundary.
                assert len(method.positional_parameters) == 2
                assert method.positional_parameters[0] == "self"
                assert len(method.parameter_annotations) == 2
                request_annotation = method.parameter_annotations[1]
                assert request_annotation is not None
                assert request_annotation.endswith(("Input", "Request"))
                assert method.return_annotation is not None
                assert method.return_annotation.startswith(("Cpn", "Workflow"))


def test__semantic_operation__nested_action_fixture_is_rejected(
    tmp_path: Path,
) -> None:
    """Prove nested independently callable classes cannot evade inventory."""
    source = (
        tmp_path / "src/python/projectkoios/workflow/petrinet/colored/nested.py"
    )
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        "class Container:\n"
        "    class HiddenAction:\n"
        "        def execute(self, request):\n"
        "            return request\n",
        encoding="utf-8",
    )
    record = discover_workflow_architecture(tmp_path)["petrinet.colored.nested"]
    # Purpose: the shared inventory exposes nested classes even though they are
    # absent from import-based SDK discovery; production policy rejects them.
    assert record.nested_class_lines == (2,)


def test__semantic_operation__identity_has_one_global_owner(
    pytestconfig: pytest.Config,
) -> None:
    """Prevent two import paths from claiming the same retained semantics."""
    root = Path(str(pytestconfig.rootpath))
    manifest = json.loads(
        (root / "docs/sdk/operation-manifest.json").read_text(encoding="utf-8")
    )
    owners_by_identity: dict[str, list[str]] = {}
    for operation in manifest["operations"]:
        owner = f"{operation['module']}:{operation['action']}"
        owners_by_identity.setdefault(operation["identity"], []).append(owner)
    duplicates = {
        identity: tuple(sorted(owners))
        for identity, owners in owners_by_identity.items()
        if len(owners) != 1
    }
    # Purpose: one action per module is insufficient if two different modules
    # claim the same semantic identity. Retained replay must resolve one owner.
    assert duplicates == {}
