#!/usr/bin/env python3
"""Generate the deterministic CPN SDK operation and signature manifest."""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import pkgutil
import sys
from enum import Enum
from pathlib import Path

PACKAGE_NAME = "projectkoios.workflow.petrinet.colored"
MANIFEST_PATH = Path("docs/sdk/operation-manifest.json")
OPERATION_METHODS = ("execute", "encode", "decode")
TASKS = (
    {
        "example": "examples/sdk/define_validate.py",
        "operations": ("CpnDefinitionValidator",),
        "task": "define-and-validate-flat-cpn",
    },
    {
        "example": "examples/sdk/execute_firing.py",
        "operations": (
            "CpnTransitionEnabler",
            "CpnBindingSelector",
            "CpnTransitionFirer",
        ),
        "task": "enable-select-and-fire",
    },
    {
        "example": "examples/sdk/canonical_replay.py",
        "operations": ("CpnCanonicalFiringResultCodec",),
        "task": "canonical-firing-result-replay",
    },
    {
        "example": "examples/sdk/payload_reference.py",
        "operations": (
            "WorkflowDomainPayloadReferenceAssembler",
            "WorkflowDomainPayloadReferenceCodec",
            "WorkflowDomainPayloadReferenceVerifier",
        ),
        "task": "retain-and-verify-opaque-payload",
    },
    {
        "example": "examples/sdk/child_plan_export.py",
        "operations": (
            "WorkflowExecutionPlanCompiler",
            "WorkflowChildDefinitionExporter",
            "WorkflowChildPlanExportCorrelator",
            "WorkflowChildPlanGraphValidator",
        ),
        "task": "compile-export-and-link-child-plan",
    },
)


def annotation_name(annotation: object) -> str:
    """Return a stable readable annotation name."""
    if annotation is inspect.Signature.empty:
        return ""
    if isinstance(annotation, str):
        return annotation
    module = getattr(annotation, "__module__", "")
    name = getattr(annotation, "__qualname__", "")
    if module and name:
        if module == "builtins":
            return name
        return f"{module}.{name}"
    return str(annotation)


def method_contract(cls: type[object], method_name: str) -> dict[str, object]:
    """Describe one public semantic method without evaluating annotations."""
    signature = inspect.signature(getattr(cls, method_name), eval_str=False)
    parameters = [
        parameter
        for name, parameter in signature.parameters.items()
        if name != "self"
    ]
    return {
        "method": method_name,
        "request_types": [
            annotation_name(parameter.annotation) for parameter in parameters
        ],
        "response_type": annotation_name(signature.return_annotation),
        "signature": str(signature),
    }


def class_kind(cls: type[object]) -> str:
    """Classify one public class for SDK discovery."""
    if issubclass(cls, Enum):
        return "enum"
    methods = {
        name for name in OPERATION_METHODS if callable(getattr(cls, name, None))
    }
    if methods == {"execute"}:
        return "action"
    if methods == {"encode", "decode"}:
        return "codec"
    if hasattr(cls, "__dataclass_fields__"):
        return "record"
    return "type"


def discover_modules() -> list[object]:
    """Import every concrete CPN SDK module in lexical order."""
    package = importlib.import_module(PACKAGE_NAME)
    names = [PACKAGE_NAME]
    names.extend(
        item.name
        for item in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + ".",
        )
        if not item.name.endswith(".__init__")
    )
    return [importlib.import_module(name) for name in sorted(set(names))]


def build_manifest() -> dict[str, object]:
    """Build the complete operation catalog and public signature snapshot."""
    operations: list[dict[str, object]] = []
    public_types: list[dict[str, object]] = []
    for module in discover_modules():
        classes = [
            value
            for name, value in vars(module).items()
            if not name.startswith("_")
            and inspect.isclass(value)
            and value.__module__ == module.__name__
        ]
        for cls in sorted(classes, key=lambda value: value.__name__):
            kind = class_kind(cls)
            type_record: dict[str, object] = {
                "kind": kind,
                "module": module.__name__,
                "name": cls.__name__,
                "signature": str(inspect.signature(cls, eval_str=False)),
                "stability": "release-candidate",
            }
            if kind == "enum":
                type_record["members"] = [
                    {"name": member.name, "value": member.value}
                    for member in cls
                ]
            public_types.append(type_record)
            if kind not in {"action", "codec"}:
                continue
            instance = cls()
            identity = instance.identity.value
            method_names = (
                ("execute",) if kind == "action" else ("encode", "decode")
            )
            operations.append(
                {
                    "action": cls.__name__,
                    "identity": identity,
                    "methods": [
                        method_contract(cls, method_name)
                        for method_name in method_names
                    ],
                    "module": module.__name__,
                    "stability": "release-candidate",
                }
            )
    public_types.sort(key=lambda item: (item["module"], item["name"]))
    operations.sort(key=lambda item: (item["module"], item["action"]))
    discovered_actions = {item["action"] for item in operations}
    task_actions = {action for task in TASKS for action in task["operations"]}
    missing_actions = sorted(task_actions - discovered_actions)
    if missing_actions:
        raise RuntimeError(
            "task index references missing actions: "
            + ", ".join(missing_actions)
        )
    return {
        "contract_namespace": "projectkoios/workflow/v0.1",
        "operations": operations,
        "package": "projectkoios-workflow",
        "public_types": public_types,
        "schema_version": 1,
        "stability": "release-candidate",
        "tasks": TASKS,
    }


def render_manifest() -> str:
    """Render canonical readable JSON for review and exact comparison."""
    return (
        json.dumps(
            build_manifest(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def main() -> int:
    """Write the manifest or report whether the checked-in file is exact."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    sys.path.insert(0, str(root / "src/python"))
    destination = root / MANIFEST_PATH
    rendered = render_manifest()
    if arguments.check:
        if not destination.exists() or destination.read_text() != rendered:
            print(f"stale SDK manifest: {destination}", file=sys.stderr)
            return 1
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
